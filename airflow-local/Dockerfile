# airflow version 2.8.1; python version 3.10
FROM apache/airflow:2.8.1-python3.10

# trao quyen cho root
USER root

# RUN: thuc thi command trong qua trinh build image
RUN apt-get update \
    && apt-get install -y --no-install-recommends docker.io \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* 

# chuyen lai sang USER airflow
USER airflow

# root --> install package --> airflow