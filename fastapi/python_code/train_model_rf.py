from sklearn import datasets
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pickle


def train():
    # chargement du jeu de données iris
    iris = datasets.load_iris()

    # création du jeu de données d'entrainement et de test
    x_train_iris, x_test_iris, y_train_iris, y_test_iris = train_test_split(iris.data, iris.target)

    np.save("./x_test_iris.npy", x_test_iris)
    np.save("./y_test_iris.npy", x_test_iris)
    
    # modèle de type RF
    clf = RandomForestClassifier()

    # entrainement du modele de type Regression
    clf.fit(x_train_iris, y_train_iris)

    # save the model to disk
    filename = './finalized_rf_model.pkl'
    with open(filename,'wb') as f:
        pickle.dump(clf, f)