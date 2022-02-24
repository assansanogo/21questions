from sklearn import datasets
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import pickle


def predict(input_data):
    # save the model to disk
    filename = './finalized_model.pkl'
    with open(filename,'rb') as f:
        clf = pickle.load(f)

    #prediction on input_data
    return clf.predict(input_data)