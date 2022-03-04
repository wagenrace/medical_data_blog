#%%
import gzip
import os
import re
import urllib.request
import pandas as pd
from time import time


result_list = []

temp_dir = "temp"
os.makedirs(temp_dir, exist_ok=True)

number = 1
number_synonyms = 0
while True:
    # Get

    file_name = f"pc_synonym_value_{str(number).zfill(6)}.ttl.gz"
    print(file_name)
    gz_file_loc = os.path.join(temp_dir, file_name)
    if not os.path.exists(gz_file_loc):
        start = time()
        download_url = fr"https://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/{file_name}"
        print("download: ", download_url)
        try:
            urllib.request.urlretrieve(download_url, gz_file_loc)
        except:
            break
        print("download time", time() - start)

    start = time()
    with gzip.open(gz_file_loc, "r") as f:
        for line in f:
            line = line.decode("utf-8")
            if line.startswith("@prefix"):
                continue
            synonym_id, _, synonym = line.split("\t")
            number_synonyms += 1
            synonym = synonym.lower()
            result = re.findall('"nsc[ -]?(\d+)"', synonym)
            # if "655363" in synonym:
            #     print(synonym)
            if result:
                result_list.append([synonym_id, result[0], synonym])
    print("reading time", time() - start)

    number += 1
print("total synonyms", number_synonyms)

result_df = pd.DataFrame(result_list, columns=["synonym_id", "NSC", "synonym"])
result_df = result_df.drop_duplicates()
result_df.to_csv(os.path.join("results", "synom_id2nsc.csv"))
