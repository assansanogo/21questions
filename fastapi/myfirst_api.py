import uvicorn
from fastapi import FastAPI
from python_code import train_model, predict_model

# initialisation
app = FastAPI()

# route
@app.get('/')
async def index():
    return {"text": "Hello API"}

@app.get('/items/{name}')
async def get_items(name):
    return {"user_name": name}

@app.get('/train')
async def trainer():
    res = train_model.train()
    return {"model_status": res}

@app.get('/predict/{features}')
async def predict(features):
    #input envoyé sous forme de texte
    features_list = [[float(el) for el in features.split(",")]]
    # prediction par le model
    res = predict_model.predict(features_list)
    # dictionnaire des classes
    classes = {0:'setosa', 1: 'versicolor', 2:'virginica'}
    # retour du resultat
    return {"predicted_class": str([classes[re] for re in res])}

if __name__ =='__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)