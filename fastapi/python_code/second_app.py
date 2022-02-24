# python_code/second_app.py
from flask import Flask
import train_model 
import predict_model
from flask import jsonify
app = Flask(__name__)

# route principale
@app.route('/')
def hello_world():
    return('Hey, we have Flask in a Docker container!')

# route prediction_vide
@app.route('/predict_empty')
def predict_dummy():
    return('Le modèle n\'est pas encore defini!')

# route entrainement_predictor
@app.route('/train')
def train_classification_model():
    train_model.train()
    return('La sauvegarde du modele est OK!')

# route predict_predictor
@app.route('/predict')
def predict_classification_model():
    # prediction retournée en liste
    preds = predict_model.predict()
    preds = [int(el) for el in preds]
    # creation de clés
    keys = [f"rep_{i}" for i in range(len(preds))]
    # combinaison des clés et valeurs
    response = dict(zip(keys, preds))
    print(response)
    # retour de la prediction
    return(jsonify(response))

# execute the app si le contexte est main
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)