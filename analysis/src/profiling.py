import polars as pl
from pathlib import Path

DATA_PATH = Path("../data")

files = [
    "Details_Itapema.csv",
    "Hosts_ids_Itapema.csv",
    "Mesh_Ids_Data_Itapema.csv",
    "Price_AV_Itapema.csv",
    "VivaReal_Itapema.csv",
]

for file in files:
    print("\n" + "=" * 80)
    print(file)

    df = pl.read_csv(DATA_PATH / file)

    print(f"Rows: {df.height:,}")
    print(f"Columns: {df.width}")

    print("\nColumns:")
    for col in df.columns:
        print(f"- {col}")

    print("\nNulls:")
    print(df.null_count())