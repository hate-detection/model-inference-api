# model-inference-api
Serving the Machine Learning model through API for inference.

> [!WARNING]
> This repo is currently at a very early stage. Many essential functionalities for an API such as Rate Limiting, Authorization etc is not yet implemented.
>
> **DO NOT USE IN PRODUCTION!!!**

## Necessary Logic

- Record input text from the client
- Pass the text through `preprocessing.py`
- Tokenize the text for BERT-based model
- Make prediction
- Send the predicted label back to the client

## Endpoints
- `/predict`: takes text as input through `POST` request and spits out the predicted label for the text. 

- `/feedback`: will record user feedback on the predicted labels through `POST` request and store it in database **[NOT YET IMPLEMENTED]** 
