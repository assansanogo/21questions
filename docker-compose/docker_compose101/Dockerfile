FROM ubuntu:devel
WORKDIR /code
ENV FLASK=app
ENV FLASK_RUN=0.0.0.0

COPY requirements.txt requirements.txt
RUN DEBIAN_FRONTEND=noninteractive apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y python3 python3-pip
RUN pip3 install -r requirements.txt
EXPOSE 5000
COPY . .
CMD ["python3", "flask_test.py"]