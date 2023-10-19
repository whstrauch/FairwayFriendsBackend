FROM python:3.10-slim-bullseye

RUN pip install --no-cache-dir --upgrade pip

WORKDIR /scoreservice
COPY ./requirements.txt /scoreservice
RUN pip install --no-cache-dir --requirement /scoreservice/requirements.txt

COPY . /scoreservice

EXPOSE 5008

CMD ["python3", "modules/main.py"]

