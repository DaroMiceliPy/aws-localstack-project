import os
from datetime import datetime
import pandas as pd
import s3fs
import boto3
import tempfile



def read_file_from_s3(bucket_name, path, format_type, **kwargs):
    file = f's3://{bucket_name}/{path}'
    fs = s3fs.S3FileSystem()
    file = fs.open(file, mode='rb')
    if format_type == 'excel':
        df = pd.read_excel(file, **kwargs)
    elif format_type == 'parquet':
        df = pd.read_parquet(file,  **kwargs)
    elif format_type == 'csv':
        df = pd.read_csv(file,  **kwargs)
    file.close()

    return df

def transform(df):
    top_10 = df.groupby("Product")["Quantity Ordered"].sum().reset_index()
    top_10 = top_10.sort_values("Quantity Ordered", ascending = False)
    top_10 = top_10.head(10).reset_index(drop=True)

    return top_10

def upload_to_s3(top_10):
    temppath = f"{tempfile.gettempdir()}/today.csv"
    top_10.to_csv(temppath, sep = ",", index = False)
    print("Llega a guardar el csv")
    year = datetime.now().strftime("%Y")
    month = datetime.now().strftime("%m")
    day = datetime.now().strftime("%d")
    path = ""
    s3 = boto3.client(
        "s3",
        region_name='us-east-1'
    )
    print("Subiendo al s3")
    s3.upload_file(Filename=temppath, Bucket="datalake", Key=f"{year}/{month}/{day}/today.csv")
    print("Subido al s3")

def main(event, context):
    bucket_name = event.get("bucket_name", None)
    path = event.get("path", None)
    format_type = event.get("format_type", None)
    print("Leyendo..")

    df = read_file_from_s3(bucket_name, path, format_type)
    top_10 = transform(df)
    upload_to_s3(top_10)

    return {"bucket": bucket_name, "path": path}
