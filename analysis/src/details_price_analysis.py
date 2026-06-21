import polars as pl
from pathlib import Path

DATA_PATH = Path("../data")
OUTPUT_PATH = Path("output")
OUTPUT_PATH.mkdir(exist_ok=True)

details = pl.read_csv(DATA_PATH / "Details_Itapema.csv")

price = (
    pl.read_csv(DATA_PATH / "Price_AV_Itapema.csv")
    .with_columns([
        pl.col("date").str.to_date().alias("stay_date"),
        pl.col("aquisition_date").str.slice(0, 10).alias("acquisition_day"),
    ])
)

# Usamos o snapshot mais recente como visão principal da análise
price_latest = price.filter(pl.col("acquisition_day") == "2025-01-20")

price_by_listing = (
    price_latest
    .group_by("airbnb_listing_id")
    .agg([
        pl.col("price").mean().round(2).alias("avg_daily_price"),
        pl.col("price").median().alias("median_daily_price"),
        pl.col("price").min().alias("min_daily_price"),
        pl.col("price").max().alias("max_daily_price"),
        pl.len().alias("priced_days"),
        pl.col("stay_date").min().alias("min_stay_date"),
        pl.col("stay_date").max().alias("max_stay_date"),
    ])
)

details_price = (
    details
    .join(price_by_listing, on="airbnb_listing_id", how="inner")
)

print("\nResumo Details + Price")
print(
    details_price.select([
        pl.len().alias("rows"),
        pl.col("airbnb_listing_id").n_unique().alias("unique_listings"),
        pl.col("avg_daily_price").mean().round(2).alias("avg_daily_price"),
        pl.col("median_daily_price").median().alias("median_daily_price"),
    ])
)

print("\nPreço por quantidade de quartos")
print(
    details_price
    .group_by("number_of_bedrooms")
    .agg([
        pl.len().alias("listings"),
        pl.col("avg_daily_price").mean().round(2).alias("avg_price"),
        pl.col("median_daily_price").median().alias("median_price"),
        pl.col("number_of_guests").median().alias("median_guests"),
    ])
    .sort("avg_price", descending=True)
)

print("\nPreço por capacidade de hóspedes")
print(
    details_price
    .group_by("number_of_guests")
    .agg([
        pl.len().alias("listings"),
        pl.col("avg_daily_price").mean().round(2).alias("avg_price"),
        pl.col("median_daily_price").median().alias("median_price"),
        pl.col("number_of_bedrooms").median().alias("median_bedrooms"),
    ])
    .sort("avg_price", descending=True)
)

print("\nPreço por tipo de imóvel")
print(
    details_price
    .group_by("listing_type")
    .agg([
        pl.len().alias("listings"),
        pl.col("avg_daily_price").mean().round(2).alias("avg_price"),
        pl.col("median_daily_price").median().alias("median_price"),
        pl.col("number_of_bedrooms").median().alias("median_bedrooms"),
        pl.col("number_of_guests").median().alias("median_guests"),
    ])
    .sort("avg_price", descending=True)
)

details_price.write_parquet(OUTPUT_PATH / "details_price_latest.parquet")

print("\nArquivo salvo em output/details_price_latest.parquet")