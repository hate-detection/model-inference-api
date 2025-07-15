# model-inference-api

<div align="center">
    <a href="overview">Overview</a> •
    <a href="necessary-logic">Necessary Logic</a> •
    <a href="installation">Installation</a> •
    <a href="usage">Usage</a> •
    <a href="self-hosting">Self Hosting</a> •
    <a href="security">Security</a> •
    <a href="cors-config">CORS Config</a>
</div>

## Overview

`model-inference-api` is a FastAPI application to serve the Machine Learning Model through an Application Programming Interface (API) for inference. This API is currently self-hosted and only accessible to the frontend application at [boli-app](https://github.com/hate-detection/boli-app).

Read on to understand the functionality, security issues mitigation, self-hosting process and CORS configuration.

## Necessary Logic

This API has two endpoints: `/predict` and `/feedback`. Both endpoints only accept `POST` requests. 

| Endpoint | Status | Objetive|
|:---------|:-------|:--------|
| `/predict`|Implemented|Takes text as input through `POST` request and spits out the predicted label for the text.|
|`/feedback`|Implemented|Records user feedback on the predicted labels through `POST` request and stores it in a PostgreSQL database.|

### Prediction Logic
- Record input text from the client
- Pass the text through `preprocessing.py`
- Tokenize the text for BERT-based model
- Make prediction
- Send the predicted label back to the client

### Feedback Logic
- Take user feedback on the predicted label
- Store the text, label along with user feedback in the database

## Installation

### Running as a docker container

>[!NOTE]
>
> This method requires you to have `docker` installed on your system

To run this app as a `docker` container, build the image using the `Dockerfile` in the root directory.

**Steps:**

1. Clone the repo (make sure to use `--recurse-submodules` as the app requires both submodules to function)
```bash
git clone --recurse-submodules https://github.com/hate-detection/model-inference-api.git

cd model-inference-api
```

2. Build the image with `Dockerfile`
```bash
docker buildx build -f Dockerfile .
```
3. Create an `.env` file with the following contents
```
REDIS_CLIENT=<redis_server_url>
POSTGRES_URL=<postgres_server_url>
API_KEY=<your_api_key>
```
4. Run the image and pass the `.env`
```
docker run --env-file /path/to/env <image_id>
```
The API server should now be running at port `9696`. To change the port or to use `gunicorn` instead of `uvicorn`, modify the `entrypoint.sh`.


### Running manually

>[!NOTE]
>
>This method requires you to have `conda` installed on your system.

This is my preferred way of running the server. I feel it gives me more control while self-hosting. 

**Steps:**

1. Clone the repo (make sure to use `--recurse-submodules` as the app requires both submodules to function)
```bash
git clone --recurse-submodules https://github.com/hate-detection/model-inference-api.git

cd model-inference-api
```
2. Create a virtual environment with `conda` and `environment.yml` and activate it
```bash
conda env create -f environment.yml
conda activate myenv
```
3. Create an `.env` file with the following contents
```
REDIS_CLIENT=<redis_server_url>
POSTGRES_URL=<postgres_server_url>
API_KEY=<your_api_key>
```
4. Run with `uvicorn` (for development) or `gunicorn` (for production)
```bash
cd app
uvicorn --host 0.0.0.0 --port 8000 main:app
```
```bash
cd app
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

## Usage

To use the `/predict` endpoint, send the following request while the server is running

```bash
curl http://localhost:8000/predict -XPOST \
-H "X-API-Key: <your_api_key" \
--json '{"text":"hello world"}'
```

To use the `/feedback` endpoint, send the following request. You should see your database tables getting populated on a successful response.
```bash
curl http://localhost:8000/feedback -XPOST \
-H "X-API-Key: <your_api_key>" \
--json '{"text":"hello world", "predicted":"1", "feedback":"1", "feedtext":"i agree"}'
```

>[!WARNING]
> 
> Ideally, the `/feedback` endpoint should **only** be used after getting a response from the `/predict` endpoint. The client should never be allowed to manipulate the `text` and `predicted` fields. You can see my implementation of this logic in [boli-app](https://github.com/hate-detection/boli-app).

## Self Hosting

## Security
- Rate Limits implemented for every endpoint.

## CORS Config
