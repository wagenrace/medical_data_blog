from os.path import join as path_join
import redis
from tqdm import tqdm
import csv
import time

r = redis.Redis(host="localhost", port=6379, db=0)

def execute_cypher(query):
    r.execute_command(
            "GRAPH.QUERY",
            "test",
            query,
        )

# Make sure database is empty
r.execute_command("DEL test")

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
