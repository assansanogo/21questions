# on construit une image de base légère
FROM nvidia/cuda:10.2-devel-ubuntu18.04 
# on construit les volumes images et logs
# ces deux volumes seront accessibles dans le container
# et sur la machine hôte 
# on copie ces fichiers dans le répertoire local
VOLUME images logs
COPY *.py ./
# commande pour réaliser les installations de librairies
# de type linux
RUN DEBIAN_FRONTEND=noninteractive apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y python3-opencv \
git python3 python3-pip keras tensorflow

# exécution du script d'entrainement
CMD python3 ./train_model.py