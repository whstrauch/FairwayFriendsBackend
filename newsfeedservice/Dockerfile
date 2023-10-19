FROM python:3.10-slim-bullseye

RUN pip install --no-cache-dir --upgrade pip

WORKDIR /newsfeedservice
COPY ./requirements.txt /newsfeedservice
RUN pip install --no-cache-dir --requirement /newsfeedservice/requirements.txt

COPY . /newsfeedservice

EXPOSE 5006

CMD ["python3", "modules/main.py"]

