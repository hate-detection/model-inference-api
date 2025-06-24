# model-inference-api
Serving the Machine Learning model through API for inference.

> [!WARNING]
> Authorization functionality is not yet implemented.
>
> **DO NOT USE IN PRODUCTION!!!**

## Necessary Logic
### Prediction Logic
- Record input text from the client
- Pass the text through `preprocessing.py`
- Tokenize the text for BERT-based model
- Make prediction
- Send the predicted label back to the client

### Feedback Logic
- Take user feedback on the predicted label
- Store the text, label along with user feedback in the database

## Endpoints
| Endpoint | Status | Objetive|
|:---------|:-------|:--------|
| `/predict`|Implemented|Takes text as input through `POST` request and spits out the predicted label for the text.|
|`/feedback`|Implemented|Records user feedback on the predicted labels through `POST` request and stores it in database.|

## Security
- Rate Limits implemented for every endpoint.
