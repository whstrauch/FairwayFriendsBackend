FROM python:3.10-slim-bullseye

RUN pip install --no-cache-dir --upgrade pip

WORKDIR /gateway
COPY ./requirements.txt /gateway
RUN pip install --no-cache-dir --requirement /gateway/requirements.txt

COPY . /gateway

EXPOSE 5000

CMD ["python3", "main.py"]

