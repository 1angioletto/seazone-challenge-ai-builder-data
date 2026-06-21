import polars as pl

df = (
    pl.read_csv("../data/Price_AV_Itapema.csv")
    .with_columns([
        pl.col("date").str.to_date().alias("stay_date"),
        pl.col("aquisition_date").str.strptime(pl.Datetime, "%Y-%m-%d %H:%M:%S%.3f").alias("acquisition_ts"),
    ])
    .with_columns([
        pl.col("acquisition_ts").dt.date().alias("acquisition_day")
    ])
)

print("\nResumo geral")
print(
    df.select([
        pl.len().alias("rows"),
        pl.col("airbnb_listing_id").n_unique().alias("unique_listings"),
        pl.col("stay_date").min().alias("min_stay_date"),
        pl.col("stay_date").max().alias("max_stay_date"),
        pl.col("acquisition_day").n_unique().alias("acquisition_days"),
    ])
)

print("\nDias de aquisição")
print(
    df.group_by("acquisition_day")
      .agg([
          pl.len().alias("rows"),
          pl.col("airbnb_listing_id").n_unique().alias("unique_listings"),
          pl.col("price").mean().round(2).alias("avg_price"),
          pl.col("price").median().alias("median_price"),
          pl.col("stay_date").min().alias("min_stay_date"),
          pl.col("stay_date").max().alias("max_stay_date"),
      ])
      .sort("acquisition_day")
)

print("\nDistribuição de preços")
print(
    df.select([
        pl.col("price").min().alias("min_price"),
        pl.col("price").quantile(0.25).alias("p25_price"),
        pl.col("price").median().alias("median_price"),
        pl.col("price").quantile(0.75).alias("p75_price"),
        pl.col("price").quantile(0.95).alias("p95_price"),
        pl.col("price").max().alias("max_price"),
    ])
)