FROM python:3.8

ADD ./app /home/app/
WORKDIR /home/app/
ENV DEBIAN_FRONTEND noninteractive
COPY requirements.txt requirements.txt
RUN apt-get update -y
RUN apt install libgl1-mesa-glx -y
RUN pip3 install -r requirements.txt

EXPOSE 5000

ENTRYPOINT ["python3", "app.py"]
