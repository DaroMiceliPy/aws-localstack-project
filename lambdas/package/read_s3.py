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
    dates = list(filter(lambda e: not isinstance(e, str), df.columns))
    strings = list(filter(lambda e: isinstance(e, str), df.columns))
    dates = [dt.strftime("%Y-%m") for dt in dates]

    new_columns = strings + dates
    df.columns = new_columns
    df.iloc[0, 1] = "Nivel General"
    df = df.drop("Unnamed: 0", axis = 1)
    df = df.rename(columns={"Unnamed: 1": "Categoria"})
    df = df[df["Categoria"].notnull()]
    df = df.T
    df.columns = df.iloc[0]
    df = df.drop(df.index[0])
    df = df.reset_index()
    df.rename(columns={"index": "date"}, inplace = True)
    df["year"] = df["date"].str.split("-").str[0]
    df["month"] = df["date"].str.split("-").str[1]
    df = df.drop("date", axis = 1)
    df.to_excel("Ver ahora.xlsx", index = False)

    return df

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
    s3.upload_file(Filename=temppath, Bucket="datalake", Key=f"{year}/{month}/today.csv")
    print("Subido al s3")

def main(event, context):
    # bucket_name = event.get("bucket_name", None)
    # path = event.get("path", None)
    # format_type = event.get("format_type", None)
    print("Leyendo..")

    df = read_file_from_s3("files-data", "inflation-rates/data.xlsx", "excel")
    df = transform(df)
    upload_to_s3(df)
