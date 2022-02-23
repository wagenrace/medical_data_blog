#%%
import gzip
import os
import urllib.request

from py2neo import Graph

temp_dir = "temp"
os.makedirs(temp_dir, exist_ok=True)

user = "neo4j"
port = "7687"
pswd = input("password")

graph = Graph("bolt://localhost:" + port, name="pubchem", auth=(user, pswd))

while True:
    # Get
    number = 1
    download_url = fr"https://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym2compound_{str(number).zfill(6)}.ttl.gz"
    print("download: ", download_url)

    gz_file = os.path.join(temp_dir, "file.gz")
    ttl_file = os.path.abspath(os.path.join(temp_dir, "file.tll"))
    try:
        urllib.request.urlretrieve(download_url, gz_file)
    except:
        break

    with gzip.open(gz_file, "r") as f:
        file_content = f.read()
        file_content = file_content.decode("utf-8")
        with open(ttl_file, "w+") as f_out:
            f_out.write(file_content)

    graph.run(f"""CALL n10s.rdf.import.fetch("file:{ttl_file}","Turtle");""")
    number += 1

while True:
    # Get
    number = 1
    download_url = fr"https://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym_value_{str(number).zfill(6)}.ttl.gz"
    print("download: ", download_url)

    gz_file = os.path.join(temp_dir, "file.gz")
    ttl_file = os.path.abspath(os.path.join(temp_dir, "file.tll"))
    try:
        urllib.request.urlretrieve(download_url, gz_file)
    except:
        break

    with gzip.open(gz_file, "r") as f:
        file_content = f.read()
        file_content = file_content.decode("utf-8")
        with open(ttl_file, "w+") as f_out:
            f_out.write(file_content)
    graph.run(f"""CALL n10s.rdf.import.fetch("file:{ttl_file}","Turtle");""")
    number += 1
