FROM python:3.12

WORKDIR /code

# Sqlite3 for debugging
RUN apt-get update && apt-get install -y sqlite3

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY init.sh /usr/local/bin/init.sh
COPY ./src /code/app

CMD ["/usr/local/bin/init.sh"]
