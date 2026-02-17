# Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install biokb_wfo
```


## With Podman/Docker

You have to install [docker](https://www.docker.com/get-started) or [podman](https://podman.io/getting-started/installation) on your system. To run all components (relational database, RESTful API server, phpMyAdmin GUI, Neo4j) ...

```bash
git clone https://github.com/biokb/biokb_wfo.git
cd biokb_wfo
python3 -m venv .venv
source .venv/bin/activate
pip install podman-compose
podman-compose --env-file .env_template up -d
```

Following services will be started:

1. RESTful API server at <a href="http://localhost:8013/docs" target="_blank">http://localhost:8013/docs</a> 
2. phpMyAdmin GUI at <a href="http://localhost:8081" target="_blank">http://localhost:8081</a> (username: biokb_user, password: biokb_password)
3. Neo4J graph database at <a href="http://localhost:7474" target="_blank">http://localhost:7474</a> (username: neo4j, password: neo4j_password)

***Tip***: Copy `.env_template` to `.env` and edit the passwords. The `.env` file is ignored by git, so your passwords will not be shared if you push your changes to the git repository and you can run the containers without `--env-file .env_template` to use your custom passwords. 
