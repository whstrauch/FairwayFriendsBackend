FROM python:3.10-slim-bullseye

RUN pip install --no-cache-dir --upgrade pip

WORKDIR /notiservice
COPY ./requirements.txt /notiservice
RUN pip install --no-cache-dir --requirement /notiservice/requirements.txt

COPY . /notiservice

EXPOSE 5007

CMD ["python3", "modules/main.py"]

