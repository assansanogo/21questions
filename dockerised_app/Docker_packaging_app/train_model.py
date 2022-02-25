import random

from config import batch_size, img_size, num_classes
from get_data_info import input_img_paths
from get_data_info import target_img_paths
from get_data_info import OxfordPets
from seg_model import get_model

from tensorflow.keras.callbacks import ModelCheckpoint, TensorBoard, EarlyStopping
import matplotlib.pyplot as plt
import numpy as np

def train():

    print("Etape 1: les données sont randomisées:\n")
    # Split our img paths into a training and a validation set
    val_samples = 1000
    rng = np.random.RandomState(42)
    rng.shuffle(input_img_paths)
    rng.shuffle(target_img_paths)

    train_input_img_paths = input_img_paths[:-val_samples]
    train_target_img_paths = target_img_paths[:-val_samples]
    val_input_img_paths = input_img_paths[-val_samples:]
    val_target_img_paths = target_img_paths[-val_samples:]
    
    print("Etape 2: les jeux de données sont préparés:\n")
    # Instantiate data Sequences for each split
    train_gen = OxfordPets(
        batch_size, img_size, train_input_img_paths, train_target_img_paths
    )
    val_gen = OxfordPets(batch_size, img_size, val_input_img_paths, val_target_img_paths)


    print("etape 3: le modèle est instantié:\n")
    net = get_model(img_size, num_classes)

    # Configurer le modèle pour l'entrainement
    # classification pixel par pixel
    net.compile(optimizer="rmsprop", 
    loss="sparse_categorical_crossentropy")

    # définition des callbacks
    # sauvegarde du modèle
    callbacks = [
        ModelCheckpoint("oxford_segmentation.h5", 
        save_best_only=True),
        TensorBoard(log_dir='/logs'),
        EarlyStopping(monitor="val_loss", min_delta = 1e-1)
    ]

    # Entrainement du modèle
    # Avec validation à la fin de chaque époch.
    # on met le paramètre de niveau de détails au maximum 
    # (barre de progrès)
    # avec verbose=1
    epochs = 10
    history = net.fit(train_gen, 
                        epochs=epochs, 
                        validation_data=val_gen, 
                        callbacks=callbacks, verbose=1)
    plt.plot(history.history["val_loss"])
    
    plt.savefig("Loss training.jpg", dpi=100)
    plt.show()

if __name__ == "__main__":
    train()

