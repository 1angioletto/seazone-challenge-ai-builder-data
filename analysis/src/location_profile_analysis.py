import polars as pl
from pathlib import Path

DATA_PATH = Path("../data")

details = pl.read_csv(DATA_PATH / "Details_Itapema.csv")

mesh = (
    pl.read_csv(DATA_PATH / "Mesh_Ids_Data_Itapema.csv")
    .sort("aquisition_date")
    .group_by("airbnb_listing_id")
    .last()
    .select(["airbnb_listing_id", "suburb"])
)

price = (
    pl.read_csv(DATA_PATH / "Price_AV_Itapema.csv")
    .with_columns([
        pl.col("date").str.to_date().alias("stay_date"),
        pl.col("aquisition_date").str.slice(0, 10).alias("acquisition_day"),
    ])
)

price_latest = price.filter(pl.col("acquisition_day") == "2025-01-20")

price_by_listing = (
    price_latest
    .group_by("airbnb_listing_id")
    .agg([
        pl.col("price").mean().round(2).alias("avg_daily_price"),
        pl.col("price").median().alias("median_daily_price"),
        pl.len().alias("priced_days"),
    ])
)

df = (
    details
    .join(mesh, on="airbnb_listing_id", how="inner")
    .join(price_by_listing, on="airbnb_listing_id", how="inner")
)

print("\nBairro + quartos")
print(
    df
    .group_by(["suburb", "number_of_bedrooms"])
    .agg([
        pl.len().alias("listings"),
        pl.col("avg_daily_price").mean().round(2).alias("avg_price"),
        pl.col("median_daily_price").median().alias("median_price"),
        pl.col("number_of_guests").median().alias("median_guests"),
    ])
    .filter(pl.col("listings") >= 10)
    .sort(["suburb", "avg_price"], descending=[False, True])
)

print("\nBairro + hóspedes")
print(
    df
    .group_by(["suburb", "number_of_guests"])
    .agg([
        pl.len().alias("listings"),
        pl.col("avg_daily_price").mean().round(2).alias("avg_price"),
        pl.col("median_daily_price").median().alias("median_price"),
        pl.col("number_of_bedrooms").median().alias("median_bedrooms"),
    ])
    .filter(pl.col("listings") >= 10)
    .sort(["suburb", "avg_price"], descending=[False, True])
)

print("\nBairro + tipo + quartos")
print(
    df
    .group_by(["suburb", "listing_type", "number_of_bedrooms"])
    .agg([
        pl.len().alias("listings"),
        pl.col("avg_daily_price").mean().round(2).alias("avg_price"),
        pl.col("median_daily_price").median().alias("median_price"),
        pl.col("number_of_guests").median().alias("median_guests"),
    ])
    .filter(pl.col("listings") >= 10)
    .sort("avg_price", descending=True)
)