FROM python:3.10-slim-bullseye

RUN pip install --no-cache-dir --upgrade pip

WORKDIR /userservice
COPY ./requirements.txt /userservice
RUN pip install --no-cache-dir --requirement /userservice/requirements.txt

COPY . /userservice

EXPOSE 5002

CMD ["python3", "modules/main.py"]

