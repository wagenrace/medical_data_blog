import gzip
import os
import re
import urllib.request
import pandas as pd


result_list = []
gz_file = r"C:\Users\tomni\Downloads\pc_synonym_value_000001.ttl.gz"

temp_dir = "temp"
os.makedirs(temp_dir, exist_ok=True)

number = 1
while True:
    # Get
    download_url = fr"https://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym_value_{str(number).zfill(6)}.ttl.gz"
    print("download: ", download_url)

    gz_file = os.path.join(temp_dir, "file.gz")
    try:
        urllib.request.urlretrieve(download_url, gz_file)
    except:
        break

    with gzip.open(gz_file, "r") as f:
        for line in f:
            line = line.decode("utf-8")
            if line.startswith("@prefix"):
                continue
            synonym_id, _, synonym = line.split("\t")
            synonym = synonym.lower()
            result = re.findall("nsc[ -]?(\d+)", synonym)
            if result:
                result_list.append([synonym_id, result[0]])

    number += 1

pd.DataFrame(result_list).to_csv(os.path.join("results", "synom_id2nsc.csv"))