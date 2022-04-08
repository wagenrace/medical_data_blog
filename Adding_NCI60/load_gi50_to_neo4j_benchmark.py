from os.path import join as path_join
from py2neo import Graph
from tqdm import tqdm
import csv
import time

user = "neo4j"
port = "7687"
pswd = input("password")

graph = Graph("bolt://localhost:" + port, auth=(user, pswd), name="test")

def execute_cypher(query):
    graph.run(
            query,
        )

# Make sure database is empty
graph.run("MATCH (n) DETACH DELETE n")

start = time.time()
with open(path_join("data", "GI50.csv"), newline="") as csvfile:
    gi50 = csv.DictReader(csvfile)
    count = 0
    for row in tqdm(gi50):
        count += 1
        execute_cypher(
            f"""
            MERGE (chem:Chemical {{nsc: {row["NSC"]}}})
            MERGE (cell:CellLine {{name: "{row["CELL_NAME"]}"}})
            MERGE (dis:Disease {{name: "{row["PANEL_NAME"]}"}})
            WITH chem, cell, dis
            MERGE (chem)-[:GI50 {{concentration: {row["AVERAGE"]}, research: "NCI60", unit: "{row["CONCENTRATION_UNIT"]}", experiment_id: "{row["EXPID"]}", count: {row["COUNT"]}}}]->(cell)
            """
        )
        if count == 1000:
            break
print(f"Creating the first {count} rows it toke {time.time() - start} seconds")

start = time.time()
for count in range(1000):
    execute_cypher(
        f"""
        MATCH (n)-[r]->(m) RETURN count(r)
        """
    )
print(f"Counting all relations {count + 1} times toke {time.time() - start} seconds")

start = time.time()
for count in range(1000):
    execute_cypher(
        f"""
        MATCH (n {{nsc: 745455}}) RETURN n
        """
    )
print(f"Find node with NSC number 745455 {count + 1} times toke {time.time() - start} seconds")
