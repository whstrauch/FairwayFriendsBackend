FROM python:3.10-slim-bullseye

RUN pip install --no-cache-dir --upgrade pip

WORKDIR /postservice
COPY ./requirements.txt /postservice
RUN pip install --no-cache-dir --requirement /postservice/requirements.txt

COPY . /postservice

EXPOSE 5003

CMD ["python3", "modules/main.py"]

