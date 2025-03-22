# moremem0 REST API Server

## Thanks Mme0ai! The majority of this project comes from their hands.

If you want to run the server with my modified version, follow the commands:

## Build Docker image
```sh
docker-compose up --build
```
### Install APOC manully 
Refer to the [realse page](https://github.com/neo4j/apoc/releases), download the `jar` package with the version of `5.26.2` and paste it into the folder you set in `docker-compose.yml`.

The default configuration is `E:/neo4j/plugins`.

> Though the latest version of Neo4j is 5.27.0, the latest version of APOC is 5.26.2 on Feb 10, 2025. So if the version of APOC catches up with that of Neo4j, you update the relevant version.Just modify the configuration in `docker-compose.yml`

### Usage

Once the server is running (locally or via Docker), you can interact with it using any REST client or through your preferred programming language (e.g., Go, Java, etc.). You can test out the APIs using the OpenAPI documentation at [`http://localhost:8000/docs`](http://localhost:8000/docs) endpoint.

Here I prepare a test file for you: `tests\test_server\test.rest`. To use it, you need to download the VS Code plugin `REST Client`. Then toggle the button floating on each http request instruction, you will see the response.

### Check the event log

When the container is running, type `docker exec -it server-app-1 /bin/bash` into your shell. You can use the command `docker ps` to list all the running container.

Then you will enter a normal Linux terminal window. The log is stored in the `~/.moremem` named `history.db`. The only thing you should do is to copy it and paste into `/app/log`. The file will appeare in the `log` folder in your root direction.