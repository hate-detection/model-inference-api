# model-inference-api

<div align="center">
    <a href="#overview">Overview</a> •
    <a href="#necessary-logic">Necessary Logic</a> •
    <a href="#installation">Installation</a> •
    <a href="#usage">Usage</a> •
    <a href="#self-hosting">Self Hosting</a> •
    <a href="#security">Security</a> •
    <a href="#cors-config">CORS Config</a> •
    <a href="#contributions">Contributions</a>
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

Apart from FastAPI specific dependencies, this project also has submodule specific dependencies. If you opt for manual installation, make sure to install these first as further steps might throw errors.

- [ ] **Java SDK (LID_tool dependency):** `sudo apt -y install default-jre`
- [ ] **Enchant library (preprocessing.py dependency):** `sudo apt-get -y install python3-enchant`
- [ ] **aspell hindi dictionary (preprocessing.py dependency):** `sudo apt-get -y install aspell-hi`
- [ ] **gcc (indic-trans dependency):**: `sudo apt-get update && apt-get -y install build-essential`


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
3. Install `indic-trans`
```bash
cd app/indic-trans
pip install -r requirements.txt
pip install .
```
4. Get `mallet` for `LID_tool`
```bash
cd app
wget https://mallet.cs.umass.edu/dist/mallet-2.0.8.tar.gz
tar -xvzf mallet-2.0.8.tar.gz
mv mallet-2.0.8 LID_tool/
rm -rf mallet-2.0.8.tar.gz
rm ._mallet-2.0.8
```
5. Create an `.env` file with the following contents
```
REDIS_CLIENT=<redis_server_url>
POSTGRES_URL=<postgres_server_url>
API_KEY=<your_api_key>
```
6. Run with `uvicorn` (for development) or `gunicorn` (for production)
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

Lucky for us, there are many ways to self-host a service today. I use Cloudflare tunnels which is the simplest and also the most efficient for my use case.

### Cloudflare Tunnel Pros:

- Super easy to set up, literally a one-line command to fire up the cloudflare tunnel as soon as your machine starts.
- Can map any internal port and service to make it publicly routable.
- Fine-grained deny-by-default security control. Lets you choose your own security mechanism.

### Cloudflare Tunnel Cons:

- The documentation does not seem too in-depth for me and there are some minor issues that wouldn't have cost me days while setting up if Cloudflare just added a little footnote in the docs.

### My Setup:
Anyways, with that out of the way, let's look into how I set up my self-host API.

- [ ] Create a free tier Cloudflare account.
- [ ] Follow the [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/) guide for initial setup.
- [ ] After setup, check if your server is accessible via the configured domain.
- [ ] If you have a frontend application like me and you want to access the backend through the frontend, it will be best to setup single header authentication. Follow the [Cloudflare guide](https://developers.cloudflare.com/cloudflare-one/identity/service-tokens/) to set it up.

**Issues I faced:**
- [ ] If you get a `This page is not redirecting properly` error, you might have to change the SSL/TLS Encryption mode to `Full (Strict)`, more in [this guide](https://developers.cloudflare.com/ssl/troubleshooting/too-many-redirects/).
- [ ] While setting up single-header authentication, I lost days wondering why is my application just ignoring the token. To fix this, go to **Zero Trust** => **Access** => **Policies**. Now add a new policy and in the **Action** dropdown, choose **Service Auth** instead of **Allow**.


## Security

Security configurations are implemented in both the FastAPI app and in the Cloudflare Tunnel policies.

### FastAPI:
- **Rate limiting via Redis:** Modify the rate-limits in `app/main.py`. Current limits are 5 requests per minute for `/` and 50 requests per minute for both `/predict` and `/feedback`.
>[!CAUTION]
>
> If you plan to use a frontend app to talk to the API Server, the rate limits should be configured in the frontend instead of the backend. Due to CORS configuration, only one origin IP will be talking to the backend, this can lead to rate limit issues on valid requests.

- **API Key authentication:** All `POST` requests to `/predict` and `/feedback` must contain a valid API Key. Set up your API Key by modifying the environment variable `API_KEY`.

### Cloudflare Tunnel

- **Service auth headers:** All requests to the tunnel should contain valid **Service auth** headers. As Cloudflare follows a deny-by-default policy, all requests without a valid header are denied access. You can set up other authentication policies via **Zero Trust** => **Access** => **Policies** in the Cloudflare dashboard.

## CORS Config

This is an optional configuration and highly dependant on the particular use case. For my setup, I only want my frontend application to communicate with my backend. My set up follows the following configuration:

### FastAPI:

- **Origins:** all
- **Headers:** all
- **Methods:** all

### Cloudflare tunnel:

- **Origins:** frontend app domain
- **Headers:** content-type, x-api-key, service auth headers
- **Methods:** POST, HEAD

## Contributions

This app is currently **not** accepting contributions. However, you are free to [fork](https://github.com/hate-detection/model-inference-api/fork) and modify the app according to your use cases. If you find a problem or have a feature recommendation, [create an issue](https://github.com/hate-detection/model-inference-api/issues).