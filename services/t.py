import pandas as pd
df = pd.read_csv("customers-100.csv")
df1 = {"name": ["A", "B"], "key": [1, 2]}
df1 = pd.DataFrame(df1)
print(list(df1.columns))
for column in df1.columns:
    print(f"{column}  : {df1[column].dtype}")