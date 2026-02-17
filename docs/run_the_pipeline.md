## Run BioKb-WFO

### From command line

If you use the command line, you can run all steps (except Neo4J import). After installation (see [Installation](installation.md)) just run:

```bash
biokb_wfo import-data
biokb_wfo create-ttls
```

Before importing into Neo4J, make sure a Neo4J instance is running (see below "[How to run Neo4J](how_to_run_neo4j.md)").

Then import into Neo4J (assuming username is `neo4j`, password is `neo4j_password` and URI is `bolt://localhost:7687`):
```bash
biokb_wfo import-neo4j -p neo4j_password
```

Login at http://localhost:7474  (user/password: neo4j/neo4j_password)

For more options see the [CLI options](cli.md) section below.


### As RESTful API server

***Usage:*** `biokb_wfo run-server [OPTIONS]`

```bash
biokb_wfo run-server
```

- ***user***: admin  
- ***password***: admin

| Option | long | Description | default |
|--------|------|-------------|---------|
| -P     | --port | API server port | 8000 |
| -u     | --user     | API username | admin   |
| -p     | --password | API password | admin | 

Service runs now at <a href="http://localhost:8000/docs" target="_blank">http://localhost:8000/docs</a> with OpenAPI documentation and interactive Swagger-UI. You can use the API to run all steps of the pipeline:

1. [Import data](http://localhost:8000/docs#/Database%20Management/import_data_import_data__post)
2. [Export ttls](http://localhost:8000/docs#/Database%20Management/get_report_export_ttls__get)
3. Run Neo4J (see below "[How to run Neo4J](#how-to-run-neo4j)")
4. [Import Neo4J](http://localhost:8000/docs#/Database%20Management/import_neo4j_import_neo4j__get)

Be patient, each step takes several minutes.


### As Podman/Docker container

For docker just replace `podman` with `docker` in the commands below.

Build & run with Podman:
```bash
git clone https://github.com/biokb/biokb_wfo.git
cd biokb_wfo
podman build -t biokb_wfo_image .
podman run -d --rm --name biokb_wfo_simple -p 8000:8000 biokb_wfo_image
```

- Login: admin  
- Password: admin

With environment variable for user and password for more security:
```bash
podman run -d --rm --name biokb_wfo_simple -p 8000:8000 -e API_PASSWORD=your_secure_password -e API_USER=your_secure_user biokb_wfo_image
```

http://localhost:8000/docs

On the website:

1. [Import data](http://localhost:8000/docs#/Database%20Management/import_data_import_data__post)
2. [Export ttls](http://localhost:8000/docs#/Database%20Management/get_report_export_ttls__get)

Neo4j import in this context is not possible because Neo4J is not running in the same network as service, but the exported turtles can be imported into any Neo4J instance using the CLI (`biokb_wfo import-neo4j`).

to stop the container:
```bash
podman stop biokb_wfo_simple
```
to rerun the container:
```bash
podman start biokb_wfo_simple
```

### As Podman/Docker networked containers

If you have docker or podman on your system, the easiest way to run all components (relational database, RESTful API server, phpMyAdmin GUI) is to use networked containers with `podman-compose`/`docker-compose`.

```bash
git clone https://github.com/biokb/biokb_wfo.git
cd biokb_wfo
podman-compose -f docker-compose.yml --env-file .env_template up -d

```
http://localhost:8000/docs

On the website:

1. [Import data](http://localhost:8000/docs#/Database%20Management/import_data_import_data__post)
2. [Export ttls](http://localhost:8000/docs#/Database%20Management/get_report_export_ttls__get)
3. [Import Neo4J](http://localhost:8000/docs#/Database%20Management/import_neo4j_import_neo4j__get)

stop with:
```bash
docker stop biokb_wfo
```

rerun with:
```bash
docker start biokb_wfo
```

***Tip***: Change the default passwords in the `.env_template` file before starting the containers for better security.
