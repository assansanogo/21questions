# on construit une image de base
FROM ubuntu:20.04
# on construit les volumes images et logs
VOLUME logs
VOLUME images
COPY *.py ./
# commande pour réaliser les installations de librairies
# de type linux
RUN DEBIAN_FRONTEND=noninteractive apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y python3-opencv python3 python3-pip 
RUN pip3 install --upgrade pip && pip3 install keras tensorflow tensorflow_datasets

# exécution du script d'entrainement
CMD python3 ./train.py