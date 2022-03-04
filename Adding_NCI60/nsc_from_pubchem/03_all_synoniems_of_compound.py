#%%
import gzip
import os
import re
import urllib.request
import pandas as pd
from time import time

temp_dir = "temp"
os.makedirs(temp_dir, exist_ok=True)

compound2nsc = pd.read_csv(os.path.join("results", "compound2nsc_full.csv"))[["compound", "NSC"]]

# Drop all compound == NaN
compound2nsc = compound2nsc.drop(compound2nsc.loc[compound2nsc.compound.isna()].index)

compound2nsc = compound2nsc.drop_duplicates()
compound2nsc = compound2nsc.set_index("compound")

result_loc = os.path.join("results", "nsc2synom_id.csv")

result_list = []

number = 1
while True:
    # Get
    file_name = f"pc_synonym2compound_{str(number).zfill(6)}.ttl.gz"
    print("working with ", file_name)
    gz_file_loc = os.path.join(temp_dir, file_name)
    if not os.path.exists(gz_file_loc):
        start = time()
        download_url = (
            fr"https://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/{file_name}"
        )
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

            if compound_id in compound2nsc.index:
                selected_compounds = compound2nsc.loc[compound_id]
                if len(selected_compounds) == 1:
                    nsc_number = selected_compounds.NSC
                    result_list.append([synonym_id, nsc_number])
                else:
                    for nsc_number in list(selected_compounds.NSC):
                        result_list.append([synonym_id, nsc_number])

    number += 1

result_df = pd.DataFrame(result_list, columns=["synonym_id", "NSC"])
result_df.to_csv(result_loc)

