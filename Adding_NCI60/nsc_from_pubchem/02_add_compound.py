#%%
import gzip
import os
import re
import urllib.request
import pandas as pd
from time import time

temp_dir = "temp"
os.makedirs(temp_dir, exist_ok=True)

result_df = pd.read_csv(os.path.join("results", "synom_id2nsc.csv"))

result_df["compound"] = None

result_df = result_df.set_index("synonym_id")

# Add compound
result_loc = os.path.join("results", "compound2nsc_full.csv")


number = 1
while True:
    # Get
    file_name = f"pc_synonym2compound_{str(number).zfill(6)}.ttl.gz"
    print("working with ", file_name)
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

    with gzip.open(gz_file_loc, "r") as f:
        for line in f:
            line = line.decode("utf-8")
            if line.startswith("@prefix"):
                continue
            synonym_id, _, compound_id_raw = line.split("\t")
            compound_id = re.findall("(compound:CID\d+)", compound_id_raw)[0]
            if synonym_id in result_df.index:
                result_df.loc[synonym_id, "compound"] = compound_id

    number += 1

result_df = result_df.drop_duplicates()
result_df.to_csv(result_loc)
