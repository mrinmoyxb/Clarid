import pandas as pd
from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from dotenv import load_dotenv
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from io import StringIO
import os
import anthropic
import uuid

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

UPLOAD_DIR = "../uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()

@app.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    print("FILE Received xxx")
    dataset_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{dataset_id}.csv")

    contents = await file.read()

    with open(file_path, "wb") as f:
        f.write(contents)

    df = pd.read_csv(file_path)
    print("FILE UPLOADED xxx")
    return {
        "dataset_id": dataset_id,
    }

@app.post("/report")
async def generate_report(payload: dict):
    print("HEllo ✅")
    dataset_id = payload.get("dataset_id")

    if not dataset_id:
        raise HTTPException(status_code=400, detail="dataset_id required")

    file_path = os.path.join(UPLOAD_DIR, f"{dataset_id}.csv")
    print("FILE PATH: ", file_path)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    df = pd.read_csv(file_path)

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

@app.post("/transform")
async def transform_dataset(payload: dict):
    dataset_id = payload.get("dataset_id")
    instruction = payload.get("instruction")

    if not dataset_id or not instruction:
        raise HTTPException(status_code=400, detail="dataset_id and instruction required")
    
    file_path = os.path.join(UPLOAD_DIR, f"{dataset_id}.csv")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    df = pd.read_csv(file_path)

    columns_str = ", ".join(
        [f"{col}({dtype})" for col, dtype in df.dtypes.astype(str).to_dict().items()]
    )

    sample_rows = df.head(2).to_string(index=False)

    prompt = f"""
        You are a data transformation engine.

        The user has a pandas dataframe called `df` with the following structure:

        Columns: {columns_str}
        Shape: {df.shape[0]} rows, {df.shape[1]} columns
        Sample:
        {sample_rows}

        The user will give you a natural language instruction.

        Return ONLY executable Python code that operates on `df`.
        Do not include imports.
        Do not include explanations.
        Do not use markdown.
        Store results back in `df` or return a value as `result`.

        User instruction:
        {instruction}
    """

    response = client.messages.create(
        model = "claude-sonnet-4-6",
        max_tokens = 500,
        temperature=0,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    generated_code = response.content[0].text.strip()
    
    restricted_globals = {
        "__builtins__": {},
        "pd": pd,
    }

    local_scope = {"df": df}

    try:
        exec(generated_code, restricted_globals, local_scope)
    except Exception as e:
        return {
            "error": "Execution failed",
            "details": str(e),
            "generated_code": generated_code
        }

    if "result" in local_scope:
        result = local_scope["result"]
    elif "df" in local_scope:
        output_df = local_scope["df"]
    else:
        return {"error": "No result produced by generated code"}
    
    response_data = output_df.head(50).to_dict(orient="records")

    return jsonable_encoder({
        "rows_returned": len(output_df),
        "preview": response_data
    })
