FROM python:3.10-slim-bullseye

RUN pip install --no-cache-dir --upgrade pip

WORKDIR /courseservice
COPY ./requirements.txt /courseservice
RUN pip install --no-cache-dir --requirement /courseservice/requirements.txt

COPY . /courseservice

EXPOSE 5005

CMD ["python3", "modules/main.py"]

