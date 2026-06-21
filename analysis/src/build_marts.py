import polars as pl
from pathlib import Path

DATA_PATH = Path("../data")
OUTPUT_PATH = Path("output")
OUTPUT_PATH.mkdir(exist_ok=True)

details = pl.read_csv(DATA_PATH / "Details_Itapema.csv")
hosts = pl.read_csv(DATA_PATH / "Hosts_ids_Itapema.csv")
mesh = pl.read_csv(DATA_PATH / "Mesh_Ids_Data_Itapema.csv")

price = (
    pl.read_csv(DATA_PATH / "Price_AV_Itapema.csv")
    .with_columns(
        pl.col("aquisition_date").str.slice(0, 10).alias("acquisition_day")
    )
)

latest_price = price.filter(pl.col("acquisition_day") == "2025-01-20")

price_summary = (
    latest_price
    .group_by("airbnb_listing_id")
    .agg([
        pl.col("price").mean().round(2).alias("avg_daily_price"),
        pl.col("price").median().alias("median_daily_price"),
        pl.col("price").min().alias("min_daily_price"),
        pl.col("price").max().alias("max_daily_price"),
        pl.len().alias("priced_days"),
    ])
)

mart = (
    details
    .join(mesh.select(["airbnb_listing_id", "suburb", "city", "state"]), on="airbnb_listing_id", how="left")
    .join(hosts, on="owner_id", how="left")
    .join(price_summary, on="airbnb_listing_id", how="left")
)

mart = mart.filter(pl.col("avg_daily_price").is_not_null())

mart.write_parquet(OUTPUT_PATH / "mart_itapema_airbnb.parquet")

print("Mart criada com sucesso")
print(f"Linhas: {mart.height:,}")
print(f"Colunas: {mart.width}")

print(
    mart.select([
        "airbnb_listing_id",
        "suburb",
        "listing_type",
        "number_of_bedrooms",
        "number_of_guests",
        "is_superhost",
        "star_rating",
        "avg_daily_price",
        "median_daily_price",
        "priced_days",
    ]).head(10)
)