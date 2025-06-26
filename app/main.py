import uvicorn
import os
import torch
import redis
import sqlalchemy
from typing import Annotated, Union
from fastapi import FastAPI, Request, Depends, Security, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader, APIKeyQuery
from slowapi import _rate_limit_exceeded_handler, Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
from peft import PeftModelForSequenceClassification
from preprocessing import PrelimProcess, TransProcess
from dotenv import load_dotenv
from sqlmodel import Field, Session, SQLModel, create_engine, select
from contextlib import asynccontextmanager


if torch.cuda.is_available():
    device = torch.device("cuda")
else:
    device = torch.device("cpu")


load_dotenv()
os.environ['TOKENIZERS_PARALLELISM'] = "false"
REDIS_CLIENT = os.getenv('REDIS_CLIENT')
POSTGRES_URL = os.getenv('POSTGRES_URL')
API_KEY = os.getenv('API_KEY')

header_scheme = APIKeyHeader(name="x-api-key", auto_error=True)

class Text(BaseModel):
    text: str


class Feedback(SQLModel, table=True):
    id: int = Field(primary_key=True)
    text: str
    predicted: int
    feedback: int
    feedtext : Union[str, None] = Field(default=None)
    approved : Union[int, None] = Field(default=None)


engine = create_engine(POSTGRES_URL)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]


def create_model():
    model_name = "google/muril-base-cased"
    model_dir = "muril_bert_adapters"
    hinglish_hate_1 = "muril_bert_adapters/hinglish_hate_1"
    hinglish_hate_2 = "muril_bert_adapters/hinglish_hate_2"

    id2label = {0: "HATE", 1: "NON-HATE"}
    label2id = {"HATE": 0, "NON-HATE": 1}


    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    base_model = AutoModelForSequenceClassification.from_pretrained(
                                                                model_name, 
                                                                num_labels=2, 
                                                                output_hidden_states=False,
                                                                id2label=id2label,
                                                                label2id=label2id 
                                                            )

    model = PeftModelForSequenceClassification.from_pretrained(
                                                                base_model,
                                                                hinglish_hate_1,
                                                                num_labels=2,
                                                                id2label=id2label,
                                                                label2id=label2id                                                
                                                            )


    model.load_adapter(hinglish_hate_1, adapter_name="hinglish_hate_1")
    model.load_adapter(hinglish_hate_2, adapter_name="hinglish_hate_2")
    model.base_model.set_adapter(["hinglish_hate_1", "hinglish_hate_2"])

    return model, tokenizer


model, tokenizer = create_model()
model.to(device)

prelim_process = PrelimProcess()
trans_process = TransProcess()


def make_prediction(text):
    cleaned_text = prelim_process.prelim_process(text)
    transformed_text = trans_process.trans_2h(cleaned_text)

    inputs = tokenizer(transformed_text, return_tensors='pt')
    
    with torch.no_grad():
        logits = model(**inputs).logits

    prediction = logits.argmax().item()

    return prediction


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

limiter = Limiter(key_func=get_remote_address, storage_uri=REDIS_CLIENT)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get('/')
@limiter.limit("5/minute")
async def index(request: Request):
    return {"wtf":"don't look here"}


@app.post('/predict')
@limiter.limit("50/minute")
async def predict(text: Text, request: Request, key: str = Depends(header_scheme)):
    print(f"Received input: {text.text}")
    label = make_prediction(str(text))
    
    return {"label": {label}}


@app.post('/feedback')
@limiter.limit("50/minute")
async def create_feedback(feedback: Feedback, request: Request, session: SessionDep, key: str = Depends(header_scheme)) -> Feedback:
    try:
        cleaned_text = prelim_process.prelim_process(feedback.text)
        transformed_text = trans_process.trans_2h(cleaned_text)
        feedback.text = transformed_text

        session.add(feedback)
        session.commit()
        session.refresh(feedback)

        return JSONResponse(content={"received": "ok"})
    
    except sqlalchemy.exc.IntegrityError:
        return JSONResponse(content={"error": "SQLAlchemy raised Integrity error, are your fields correct?"})



if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=9696)
