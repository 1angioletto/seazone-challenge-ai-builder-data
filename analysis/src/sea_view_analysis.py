import polars as pl
from pathlib import Path

DATA_PATH = Path("../data")

SEA_VIEW_TERMS = [
    "vista mar",
    "vista para o mar",
    "vista do mar",
    "frente mar",
    "frente ao mar",
    "beira mar",
    "beira-mar",
    "pé na areia",
    "pe na areia",
    "quadra mar",
    "quadra do mar",
    "orla",
    "ocean view",
    "sea view",
    "beachfront",
    "waterfront",
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
        pl.len().alias("priced_days"),
    ])
)

details_features = (
    details
    .with_columns([
        (
            has_term_expr("ad_name")
            | has_term_expr("ad_description")
            | has_term_expr("space")
            | has_term_expr("amenities")
        ).alias("has_sea_view_text")
    ])
)

df = (
    details_features
    .join(mesh, on="airbnb_listing_id", how="inner")
    .join(price_by_listing, on="airbnb_listing_id", how="inner")
)

print("\nVista mar textual vs preço")
print(
    df
    .group_by("has_sea_view_text")
    .agg([
        pl.len().alias("listings"),
        pl.col("avg_daily_price").mean().round(2).alias("avg_price"),
        pl.col("median_daily_price").median().alias("median_price"),
        pl.col("number_of_bedrooms").median().alias("median_bedrooms"),
        pl.col("number_of_guests").median().alias("median_guests"),
    ])
    .sort("avg_price", descending=True)
)

print("\nVista mar por bairro")
print(
    df
    .group_by(["suburb", "has_sea_view_text"])
    .agg([
        pl.len().alias("listings"),
        pl.col("avg_daily_price").mean().round(2).alias("avg_price"),
        pl.col("median_daily_price").median().alias("median_price"),
        pl.col("number_of_bedrooms").median().alias("median_bedrooms"),
        pl.col("number_of_guests").median().alias("median_guests"),
    ])
    .filter(pl.col("listings") >= 5)
    .sort(["suburb", "avg_price"], descending=[False, True])
)

print("\nTop anúncios com indicação de vista mar")
print(
    df
    .filter(pl.col("has_sea_view_text") == True)
    .select([
        "airbnb_listing_id",
        "suburb",
        "ad_name",
        "number_of_bedrooms",
        "number_of_guests",
        "avg_daily_price",
        "median_daily_price",
    ])
    .sort("avg_daily_price", descending=True)
    .head(20)
)