import pandas as pd
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from io import StringIO

app = FastAPI()

class DataInput(BaseModel):
    data: list

@app.post("/report")
async def generate_report(file: UploadFile = File(...)):
    df = pd.DataFrame(input.data)
    contents = await file.read()
    s = str(contents, "utf-8")

    df = pd.read_csv(StringIO(s))
    report = {}

    report["row_count"] = len(df)
    report["column_count"] = len(df.columns)

    report["missing_values"] = df.isnull().sum().to_dict()
    report["duplicate_rows"] = df.duplicated().sum()

    whitespace_issues = {}
    for col in df.select_dtypes(include=["object"]).columns:
        whitespace_issues[col] = df[col].apply(
            lambda x: isinstance(x, str) and (x != x.strip())
        ).sum()
    report["whitespace_issues"] = whitespace_issues
    report["data_types"] = df.dtypes.astype(str).to_dict()

    return report

@app.post("/clean")
def clean_data(input: DataInput):
    df = pd.DataFrame(input.data)
