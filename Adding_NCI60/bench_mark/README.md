# Benchmark Redis graph VS neo4j

The query is sub optimal so that could be the problem.

## Redis

```
docker run -p 6379:6379 -it --rm redislabs/redisgraph
```

```
Creating the first 1000 rows it toke 2.1248602867126465 seconds
Counting all relations 1000 times toke 1.2885651588439941 seconds
Find node with NSC number 745455 1000 times toke 1.149787187576294 seconds
``` 

## Neo4j setup

Neo4j desktop

```
Creating the first 1000 rows it toke 35.65673303604126 seconds
Counting all relations 1000 times toke 1.298534870147705 seconds
Find node with NSC number 745455 1000 times toke 1.4073879718780518 seconds
```