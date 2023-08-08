FROM apache/airflow:latest-python3.10

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY ./dags /app/dags
COPY ./src /app/src

CMD ["airflow", "standalone"]