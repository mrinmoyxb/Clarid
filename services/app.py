import pandas as pd
from fastapi import FastAPI, Request, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from io import StringIO
import os
import anthropic

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

UPLOAD_DIR = "uploads"
os.mkdir(UPLOAD_DIR, exist_ok = True)

app = FastAPI()

@app.post("/report")
async def generate_report(request: Request):
    body = await request.body()
    s = body.decode("utf-8", errors="ignore")
    df = pd.read_csv(StringIO(s))

    report = {}
    datasetOverview = {}

    datasetOverview["row_count"] = int(len(df))
    datasetOverview["column_count"] = int(len(df.columns))
    datasetOverview["estimated_memory_usage_bytes"] = int(df.memory_usage(deep=True).sum())
    datasetOverview["column_names"] = list(df.columns)
    datasetOverview["column_names_dtype"] = df.dtypes.astype(str).to_dict()
    report["dataset_overview"] = datasetOverview

    report["missing_values"] = { col: int(val) for col, val in df.isnull().sum().to_dict().items() }
    report["duplicate_rows"] = int(df.duplicated().sum())

    whitespace_issues = {}
    for col in df.select_dtypes(include=["object"]).columns:
        whitespace_issues[col] = int(df[col].apply(
            lambda x: isinstance(x, str) and (x != x.strip())
        ).sum())
    report["whitespace_issues"] = whitespace_issues

    return jsonable_encoder(report)

    
    
