#%%
import gzip
import os
import re
import urllib.request
import pandas as pd
from time import time


temp_dir = "temp"
os.makedirs(temp_dir, exist_ok=True)
nsc2synom = pd.read_csv(os.path.join("results", "nsc2synom_id.csv"))[["synonym_id", "NSC"]]

# Some synonyms have multiple nsc number
nsc2synom = nsc2synom.set_index('synonym_id')
grouped_nsc = nsc2synom.groupby('synonym_id')["NSC"].apply(list)

# Dict are way faster to lookup in as dataframes
synom_id2nsc = grouped_nsc.to_dict()

# Appending to a list is way faster as updating a dataframe
result_list = []

result_loc = os.path.join("results", "nsc2synonym.csv")

number = 1
while True:
    # Get
    file_name = f"pc_synonym_value_{str(number).zfill(6)}.ttl.gz"
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
    number_lines = 0
    with gzip.open(gz_file_loc, "r") as f:
        for line in f:
            line = line.decode("utf-8")
            if line.startswith("@prefix"):
                continue
            synonym_id, _, synonym = line.split("\t")
            synonym = synonym.lower()

            result = re.findall('"(.*)"@', synonym)[0]
            nsc_numbers = synom_id2nsc.get(synonym_id, [])
            if result:
                for nsc in nsc_numbers:
                    result_list.append([result, nsc])
            number_lines += 1
            if number_lines % 10000 == 0:
                print(f"reading time {number_lines}: {time() - start}")

    print("reading time", time() - start)

    number += 1

result_df = pd.DataFrame(result_list, columns=["synonym", "NSC"])
result_df.to_csv(result_loc)