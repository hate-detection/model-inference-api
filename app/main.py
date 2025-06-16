import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
from peft import PeftModelForSequenceClassification
from preprocessing import PrelimProcess, TransProcess
import os 

os.environ['TOKENIZERS_PARALLELISM'] = "false"

app = FastAPI()

class Text(BaseModel):
    text: str

model_name = "google/muril-base-cased"
model_dir = "muril_bert_adapters"
hinglish_hate_1 = "muril_bert_adapters/hinglish_hate_1"
hinglish_hate_2 = "muril_bert_adapters/hinglish_hate_2"

id2label = {0: "HATE", 1: "NON-HATE"}
label2id = {"HATE": 0, "NON-HATE": 1}

if torch.cuda.is_available():
    device = torch.device("cuda")
else:
    device = torch.device("cpu")


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


@app.get('/')
async def index():
    return {"wtf":"don't look here"}


@app.post('/predict')
async def predict(text: Text):
    print(f"Received input: {text.text}")
    label = make_prediction(str(text))
    
    return {"label": {label}}



if __name__ == '__main__':
    uvicorn.run(app,host="127.0.0.1", port=9696)
