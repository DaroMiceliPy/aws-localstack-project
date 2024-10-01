FROM apache/airflow:2.0.1

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libsnappy-dev \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow
COPY requirements.txt /requirements.txt
RUN pip install --user --upgrade pip
RUN pip install --no-cache-dir --user -r /requirements.txt