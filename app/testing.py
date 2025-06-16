from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_normal_predict():
    data = {'text': 'Muslims have good Jawline, kyunki unka muslim hota hai.'}
    response = client.post("/predict",
                            json=data,
                            headers={'Content-Type': 'application/json' }
                        )
    result = response.json()
    assert response.status_code == 200
    assert result == {'label': [1]}



def test_hate_predict():
    data = {'text': 'old video saar, last time also mulle got piped this time also mulle got piped #LMFAO'}
    response = client.post("/predict",
                            json=data,
                            headers={'Content-Type': 'application/json' }
                        )
    result = response.json()
    assert response.status_code == 200
    assert result == {'label': [0]}