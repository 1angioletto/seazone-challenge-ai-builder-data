import polars as pl
from pathlib import Path

DATA_PATH = Path("../data")

SEA_VIEW_TERMS = [
    "vista mar", "vista para o mar", "vista do mar",
    "frente mar", "frente ao mar",
    "beira mar", "beira-mar",
    "pé na areia", "pe na areia",
    "quadra mar", "quadra do mar",
    "orla",
    "ocean view", "sea view", "beachfront", "waterfront",
]

def has_term_expr(col_name: str) -> pl.Expr:
    text = pl.col(col_name).cast(pl.Utf8).fill_null("").str.to_lowercase()
    expr = pl.lit(False)

    for term in SEA_VIEW_TERMS:
        expr = expr | text.str.contains(term, literal=True)

    return expr

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
        pl.col("price").min().alias("min_daily_price"),
        pl.col("price").max().alias("max_daily_price"),
        pl.len().alias("priced_days"),
    ])
)

df = (
    details
    .with_columns([
        (
            has_term_expr("ad_name")
            | has_term_expr("ad_description")
            | has_term_expr("space")
            | has_term_expr("amenities")
        ).alias("has_sea_view_text")
    ])
    .join(mesh, on="airbnb_listing_id", how="inner")
    .join(price_by_listing, on="airbnb_listing_id", how="inner")
)

morretes = df.filter(pl.col("suburb") == "Morretes")

print("\nResumo Morretes")
print(
    morretes.select([
        pl.len().alias("listings"),
        pl.col("avg_daily_price").mean().round(2).alias("avg_price"),
        pl.col("avg_daily_price").median().alias("median_avg_price"),
        pl.col("avg_daily_price").quantile(0.25).alias("p25_avg_price"),
        pl.col("avg_daily_price").quantile(0.75).alias("p75_avg_price"),
        pl.col("avg_daily_price").quantile(0.95).alias("p95_avg_price"),
        pl.col("avg_daily_price").max().alias("max_avg_price"),
    ])
)

print("\nMorretes com e sem vista mar")
print(
    morretes
    .group_by("has_sea_view_text")
    .agg([
        pl.len().alias("listings"),
        pl.col("avg_daily_price").mean().round(2).alias("avg_price"),
        pl.col("avg_daily_price").median().alias("median_avg_price"),
        pl.col("avg_daily_price").quantile(0.75).alias("p75_avg_price"),
        pl.col("avg_daily_price").max().alias("max_avg_price"),
        pl.col("number_of_bedrooms").median().alias("median_bedrooms"),
        pl.col("number_of_guests").median().alias("median_guests"),
    ])
    .sort("avg_price", descending=True)
)

print("\nMorretes por quartos")
print(
    morretes
    .group_by("number_of_bedrooms")
    .agg([
        pl.len().alias("listings"),
        pl.col("avg_daily_price").mean().round(2).alias("avg_price"),
        pl.col("avg_daily_price").median().alias("median_avg_price"),
        pl.col("avg_daily_price").max().alias("max_avg_price"),
        pl.col("number_of_guests").median().alias("median_guests"),
        pl.col("has_sea_view_text").sum().alias("sea_view_count"),
    ])
    .sort("avg_price", descending=True)
)

print("\nTop 20 imóveis Morretes por preço médio")
print(
    morretes
    .select([
        "airbnb_listing_id",
        "ad_name",
        "listing_type",
        "number_of_bedrooms",
        "number_of_guests",
        "has_sea_view_text",
        "avg_daily_price",
        "median_daily_price",
        "min_daily_price",
        "max_daily_price",
        "priced_days",
    ])
    .sort("avg_daily_price", descending=True)
    .head(20)
)

# Remove outliers acima do percentil 95 de Morretes
p95 = morretes.select(pl.col("avg_daily_price").quantile(0.95)).item()

morretes_no_outliers = morretes.filter(pl.col("avg_daily_price") <= p95)

print(f"\nResumo Morretes sem outliers acima do P95: {p95:.2f}")
print(
    morretes_no_outliers.select([
        pl.len().alias("listings"),
        pl.col("avg_daily_price").mean().round(2).alias("avg_price"),
        pl.col("avg_daily_price").median().alias("median_avg_price"),
        pl.col("avg_daily_price").quantile(0.75).alias("p75_avg_price"),
        pl.col("avg_daily_price").max().alias("max_avg_price"),
    ])
)

print("\nMorretes sem outliers: com e sem vista mar")
print(
    morretes_no_outliers
    .group_by("has_sea_view_text")
    .agg([
        pl.len().alias("listings"),
        pl.col("avg_daily_price").mean().round(2).alias("avg_price"),
        pl.col("avg_daily_price").median().alias("median_avg_price"),
        pl.col("avg_daily_price").max().alias("max_avg_price"),
        pl.col("number_of_bedrooms").median().alias("median_bedrooms"),
        pl.col("number_of_guests").median().alias("median_guests"),
    ])
    .sort("avg_price", descending=True)
)