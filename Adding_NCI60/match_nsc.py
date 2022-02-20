#%%
from py2neo import Graph
import pandas as pd
from os.path import join as path_join
from tqdm import tqdm

chem_names = pd.read_csv(
    path_join("data", "chemnames_Aug2013.txt"),
    "|",
    header=None,
    names=["NSC", "Name", "Name Type"],
)
GI50 = pd.read_csv(path_join("data", "GI50.csv"))

all_nsc = GI50["NSC"].unique()

user = "neo4j"
port = "7687"
pswd = input("password")

graph = Graph("bolt://localhost:" + port, auth=(user, pswd))
results = pd.DataFrame(columns=["NSC", "MeshLabel", "MeshType", "MeshNumResults", "NumberTerms"])

for nsc_number in tqdm(all_nsc[:500]):
    all_chem_names = chem_names.loc[chem_names["NSC"] == nsc_number]["Name"]
    all_chem_names = [i.lower() for i in all_chem_names]
    nsc_names = [f"nsc{nsc_number}", f"nsc {nsc_number}", f"nsc-{nsc_number}"]
    all_synonyms = all_chem_names + nsc_names
    cypher_all_synonyms = f"""[{','.join([f'"{i}"' for i in all_synonyms])}]"""

    # Find all terms
    response = graph.run(
        f"""MATCH (t:ns0__Term) WHERE toLower(t.ns0__prefLabel) IN {cypher_all_synonyms} RETURN count(t) as num_terms"""
    ).data()
    num_terms = response[0]["num_terms"]
    if num_terms == 0:
        results = results.append(
            {
                "NSC": nsc_number,
                "MeshLabel": None,
                "MeshType": None,
                "MeshNumResults": 0,
                "NumberTerms": num_terms,
            },
            ignore_index=True,
        )
        continue

    # Find preferred concept
    response = graph.run(
        f"""MATCH (t:ns0__Term)-[*1..2]-(preferred_concepts:ns0__Concept)<-[:ns0__preferredConcept]-(:ns0__TopicalDescriptor) WHERE toLower(t.ns0__prefLabel) IN {cypher_all_synonyms} RETURN preferred_concepts"""
    ).data()
    all_labels = [i["preferred_concepts"]["rdfs__label"] for i in response]
    unique_labels = list(set(all_labels))
    num_concepts = len(unique_labels)
    if num_concepts > 0:
        # count labels
        label_count = {}
        for label in unique_labels:
            label_count[label] = all_labels.count(label)
        most_common_label = max(label_count, key=lambda x: label_count[x])
        results = results.append(
            {
                "NSC": nsc_number,
                "MeshLabel": most_common_label,
                "MeshType": "Concept",
                "MeshNumResults": num_concepts,
                "NumberTerms": num_terms,
            },
            ignore_index=True,
        )
        continue
    
    # Find preferred SCR Chemical
    response = graph.run(
        f"""MATCH (t:ns0__Term)-[*1..2]-(c:ns0__Concept)<-[:ns0__preferredConcept]-(preferred_scr:ns0__SCR_Chemical) WHERE toLower(t.ns0__prefLabel) IN {cypher_all_synonyms} RETURN preferred_scr"""
    ).data()
    all_labels = [i["preferred_scr"]["rdfs__label"] for i in response]
    unique_labels = list(set(all_labels))
    num_scr = len(unique_labels)
    if num_scr > 0:
        # count labels
        label_count = {}
        for label in unique_labels:
            label_count[label] = all_labels.count(label)
        most_common_label = max(label_count, key=lambda x: label_count[x])
        results = results.append(
            {
                "NSC": nsc_number,
                "MeshLabel": most_common_label,
                "MeshType": "SCR_Chemical",
                "MeshNumResults": num_scr,
                "NumberTerms": num_terms,
            },
            ignore_index=True,
        )
        continue

    # No results found
    results = results.append(
            {
                "NSC": nsc_number,
                "MeshLabel": None,
                "MeshType": None,
                "MeshNumResults": 0,
                "NumberTerms": num_terms,
            },
            ignore_index=True,
        )
results.to_csv(path_join("results", "nsc_gi502mesh.csv"))
