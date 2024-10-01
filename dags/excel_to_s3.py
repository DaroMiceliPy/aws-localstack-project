from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.decorators import task
from airflow.hooks.S3_hook import S3Hook
import pickle
import datetime as dt
import os
import pandas as pd
from airflow.providers.amazon.aws.hooks import lambda_function

with DAG(
    dag_id="excel_to_s3",
    start_date=dt.datetime(2020, 1, 1),
    schedule_interval="1 12 7 * *",
    catchup=False
) as dag:

    @task
    def create_folder():
        try:
            os.mkdir("tmp")
            return "/tmp/"
        except FileExistsError:
            print("The folder exists")
            return "/tmp/"

    @task
    def download_excel_to_s3(tmp):
        df = pd.read_excel("https://www.estadisticaciudad.gob.ar/eyc/wp-content/uploads/2024/07/IPCBA_base_2021100-Incidencia_div_niv_gral.xlsx", skiprows=2, engine="openpyxl")
        df.to_excel(f"{tmp}data.xlsx", index=False)

        return f"{tmp}data.xlsx"

    @task
    def upload_to_s3(path_excel):
        hook = S3Hook("aws_localstack")
        hook.load_file(
            filename=path_excel,
            key="inflation-rates/data.xlsx",
            bucket_name="files-data",
            replace=True
        )

    tmp = create_folder()
    path_excel = download_excel_to_s3(tmp)
    upload_to_s3(path_excel)
