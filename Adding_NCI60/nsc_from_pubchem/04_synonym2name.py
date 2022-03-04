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
nsc2synom = nsc2synom.set_index("synonym_id")
nsc2synom["synonym"] = None

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
    with gzip.open(gz_file_loc, "r") as f:
        for line in f:
            line = line.decode("utf-8")
            if line.startswith("@prefix"):
                continue
            synonym_id, _, synonym = line.split("\t")
            synonym = synonym.lower()

            result = re.findall('"(.*)"@', synonym)[0]
            if synonym_id in nsc2synom.index and result:
                nsc2synom.loc[synonym_id, "synonym"] = result

    print("reading time", time() - start)

    number += 1

result_df = nsc2synom[["synonym", "NSC"]]
result_df.to_csv(result_loc)