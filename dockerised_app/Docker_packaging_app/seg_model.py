from tensorflow.keras import layers
from tensorflow.keras.models import Model
from tensorflow.keras import backend as K
from config import img_size,num_classes


def get_model(img_size, num_classes):
    """
    fonction qui crée le modèle de deep learning 
    (modèle de segmentation UNET)
    """
    inputs = layers.Input(shape=img_size + (3,))

    ### première partie: downsampling = réduction de la dimension
    # de  l'image ###

    # Entry block/bloc d'entrée
    x = layers.Conv2D(32, 3, strides=2, padding="same")(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)

    previous_block_activation = x  
    
    #on stocke x dans une variable "le résidu"

    # Blocks 1, 2, 3 are identical apart from the feature depth.
    for filters in [64, 128, 256]:
        x = layers.Activation("relu")(x)
        x = layers.SeparableConv2D(filters, 3, padding="same")(x)
        x = layers.BatchNormalization()(x)

        x = layers.Activation("relu")(x)
        x = layers.SeparableConv2D(filters, 3, padding="same")(x)
        x = layers.BatchNormalization()(x)

        x = layers.MaxPooling2D(3, strides=2, padding="same")(x)

        # Project residual
        residual = layers.Conv2D(filters, 1, strides=2, padding="same")(
            previous_block_activation
        )
        x = layers.add([x, residual])  # On ajoute le résidu x
        previous_block_activation = x  # Set aside next residual

    ### première partie: downsampling = augmentation de la dimension
    # de l'image###

    for filters in [256, 128, 64, 32]:
        x = layers.Activation("relu")(x)
        x = layers.Conv2DTranspose(filters, 3, padding="same")(x)
        x = layers.BatchNormalization()(x)

        x = layers.Activation("relu")(x)
        x = layers.Conv2DTranspose(filters, 3, padding="same")(x)
        x = layers.BatchNormalization()(x)

        x = layers.UpSampling2D(2)(x)

        # Project residual
        residual = layers.UpSampling2D(2)(previous_block_activation)
        residual = layers.Conv2D(filters, 1, padding="same")(residual)
        x = layers.add([x, residual])  # Add back residual
        previous_block_activation = x  # Set aside next residual

    # On ajoute une couche de classification 
    # (avec autant de couches qu'il y a de classes qu'il y a)
    outputs = layers.Conv2D(num_classes, 3, activation="softmax", padding="same")(x)

    # Define the model
    model = Model(inputs, outputs)
    return model


# libère la RAM occuppée RAM si le modèle a été défini plusieurs fois
# (impactant lorsque vous développez dans COLAB ou Jupyter notebook)
K.clear_session()

# Build model
model = get_model(img_size, num_classes)
#  afficher la structure du modèle
print(model.summary())
