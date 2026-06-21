import polars as pl
from pathlib import Path

DATA_PATH = Path("../data")

details = pl.read_csv(DATA_PATH / "Details_Itapema.csv")

hosts = (
    pl.read_csv(DATA_PATH / "Hosts_ids_Itapema.csv")
    .group_by("owner_id")
    .last()
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
    .join(hosts, on="owner_id", how="left")
    .join(price_by_listing, on="airbnb_listing_id", how="inner")
)

print("\nResumo geral")
print(
    df.select([
        pl.len().alias("rows"),
        pl.col("airbnb_listing_id").n_unique().alias("unique_listings"),
        pl.col("owner_id").n_unique().alias("unique_hosts"),
        pl.col("avg_daily_price").mean().round(2).alias("avg_price"),
        pl.col("median_daily_price").median().alias("median_price"),
    ])
)

print("\nSuperhost vs não superhost")
print(
    df
    .group_by("is_superhost")
    .agg([
        pl.len().alias("listings"),
        pl.col("owner_id").n_unique().alias("hosts"),
        pl.col("avg_daily_price").mean().round(2).alias("avg_price"),
        pl.col("median_daily_price").median().alias("median_price"),
        pl.col("star_rating").median().alias("median_listing_rating"),
        pl.col("number_of_reviews").median().alias("median_listing_reviews"),
    ])
    .sort("avg_price", descending=True)
)

print("\nExperiência do host por faixa")
df_exp = df.with_columns(
    pl.when(pl.col("years_host") < 1).then(pl.lit("0-1 ano"))
    .when(pl.col("years_host") < 3).then(pl.lit("1-3 anos"))
    .when(pl.col("years_host") < 5).then(pl.lit("3-5 anos"))
    .otherwise(pl.lit("5+ anos"))
    .alias("host_experience_bucket")
)

print(
    df_exp
    .group_by("host_experience_bucket")
    .agg([
        pl.len().alias("listings"),
        pl.col("owner_id").n_unique().alias("hosts"),
        pl.col("avg_daily_price").mean().round(2).alias("avg_price"),
        pl.col("median_daily_price").median().alias("median_price"),
        pl.col("star_rating").median().alias("median_listing_rating"),
    ])
    .sort("avg_price", descending=True)
)

print("\nReviews do listing por faixa")
df_reviews = df.with_columns(
    pl.when(pl.col("number_of_reviews") == 0).then(pl.lit("0"))
    .when(pl.col("number_of_reviews") <= 10).then(pl.lit("1-10"))
    .when(pl.col("number_of_reviews") <= 50).then(pl.lit("11-50"))
    .when(pl.col("number_of_reviews") <= 100).then(pl.lit("51-100"))
    .otherwise(pl.lit("100+"))
    .alias("listing_reviews_bucket")
)

print(
    df_reviews
    .group_by("listing_reviews_bucket")
    .agg([
        pl.len().alias("listings"),
        pl.col("avg_daily_price").mean().round(2).alias("avg_price"),
        pl.col("median_daily_price").median().alias("median_price"),
        pl.col("star_rating").median().alias("median_rating"),
    ])
    .sort("avg_price", descending=True)
)