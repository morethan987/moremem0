# Mem0 REST API Server

Mem0 provides a REST API server (written using FastAPI). Users can perform all operations through REST endpoints. The API also includes OpenAPI documentation, accessible at `/docs` when the server is running.

## Features

- **Create memories:** Create memories based on messages for a user, agent, or run.
- **Retrieve memories:** Get all memories for a given user, agent, or run.
- **Search memories:** Search stored memories based on a query.
- **Update memories:** Update an existing memory.
- **Delete memories:** Delete a specific memory or all memories for a user, agent, or run.
- **Reset memories:** Reset all memories for a user, agent, or run.
- **OpenAPI Documentation:** Accessible via `/docs` endpoint.

## Running Locally

### With Docker

1. Create a `.env` file in the root directory of the project and set your environment variables. For example:

```env
OPENAI_API_KEY=your-openai-api-key
```

2. Build the Docker image:

```bash
docker build -t mem0-api-server .
```

3. Run the Docker container:

``` bash
docker run -p 8000:8000 mem0-api-server
```

4. Access the API at http://localhost:8000.

### Without Docker

1. Create a `.env` file in the root directory of the project and set your environment variables. For example:

```env
OPENAI_API_KEY=your-openai-api-key
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the FastAPI server:

```bash
uvicorn main:app --reload
```

4. Access the API at http://localhost:8000.

### Usage

Once the server is running (locally or via Docker), you can interact with it using any REST client or through your preferred programming language (e.g., Go, Java, etc.). You can test out the APIs using the OpenAPI documentation at [`http://localhost:8000/docs`](http://localhost:8000/docs) endpoint.
