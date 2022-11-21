FROM python:3.7

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

WORKDIR /code/app

CMD [ "uvicorn", "main:app", "--ssl-keyfile","127.0.0.1+1-key.pem", "--host", "0.0.0.0", "--ssl-certfile",  "127.0.0.1+1.pem", "--log-level", "trace"]
