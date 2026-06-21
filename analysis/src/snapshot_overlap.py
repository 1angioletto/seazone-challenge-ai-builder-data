import polars as pl

df = (
    pl.read_csv("../data/Price_AV_Itapema.csv")
    .with_columns(
        pl.col("aquisition_date")
        .str.slice(0, 10)
        .alias("snapshot")
    )
)

overlap = (
    df.group_by("airbnb_listing_id")
      .agg(
          pl.col("snapshot").n_unique().alias("snapshot_count")
      )
)

print(
    overlap.group_by("snapshot_count")
           .agg(pl.len().alias("listings"))
           .sort("snapshot_count")
)

print("\nImóveis presentes nos 3 snapshots:")

print(
    overlap
    .filter(pl.col("snapshot_count") == 3)
    .height
)