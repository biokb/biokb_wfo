# How to run Neo4J

To run Neo4J separately.

For docker just replace `podman` with `docker` in the commands below.
```bash
podman run -d --rm --name neo4j-test -p7474:7474 -p7687:7687 -e NEO4J_AUTH=neo4j/neo4j_password neo4j:latest
```

Remove `--rm` if you want to keep the container after stopping it.

Neo4J is then available at:
<a href="http://localhost:7474" target="_blank">http://localhost:7474</a>  (user/password: neo4j/neo4j_password

Stop Neo4J with:

```bash
podman stop biokb-neo4j
```
if you have not used `--rm` above, you can restart Neo4J with:
```bash
podman start biokb-neo4j