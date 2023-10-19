FROM python:3.10-slim-bullseye

RUN pip install --no-cache-dir --upgrade pip

WORKDIR /authservice
COPY ./requirements.txt /authservice
RUN pip install --no-cache-dir --requirement /authservice/requirements.txt

COPY . /authservice

EXPOSE 5001

CMD ["python3", "modules/main.py"]

