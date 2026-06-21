from pathlib import Path
import re
import polars as pl


DETAILS_PATH = Path("../data/Details_Itapema.csv")
PRICE_PATH = Path("../data/Price_AV_Itapema.csv")
MESH_PATH = Path("../data/Mesh_Ids_Data_Itapema.csv")
VIVAREAL_PATH = Path("../data/VivaReal_Itapema.csv")

OUTPUT_DIR = Path("output")

UNITS = 50
UNIT_SIZE_M2 = 100
OCCUPANCY_RATE = 0.62
OPERATING_COST_RATE = 0.35

DAILY_RATE_GROWTH = {
    2025: 0.00,
    2026: 0.08,
    2027: 0.16,
}


def normalize_text(value: str) -> str:
    if value is None:
        return ""

    value = str(value).lower().strip()

    replacements = {
        "à": "a", "á": "a", "â": "a", "ã": "a",
        "é": "e", "ê": "e",
        "í": "i",
        "ó": "o", "ô": "o", "õ": "o",
        "ú": "u",
        "ç": "c",
    }

    for old, new in replacements.items():
        value = value.replace(old, new)

    value = re.sub(r"\s+", " ", value)

    return value


def clean_money(value) -> float | None:
    if value is None:
        return None

    value = str(value).lower()
    value = re.sub(r"[^0-9,\.]", "", value)

    if value == "":
        return None

    if "," in value and "." in value:
        value = value.replace(".", "").replace(",", ".")
    elif "," in value:
        value = value.replace(",", ".")

    try:
        return float(value)
    except ValueError:
        return None


def clean_number(value) -> float | None:
    if value is None:
        return None

    value = str(value)
    value = re.sub(r"[^0-9,\.]", "", value)

    if value == "":
        return None

    value = value.replace(",", ".")

    try:
        return float(value)
    except ValueError:
        return None


def load_airbnb_region_revenue() -> pl.DataFrame:
    details = pl.read_csv(DETAILS_PATH, infer_schema_length=10000)
    prices = pl.read_csv(PRICE_PATH, infer_schema_length=10000)
    mesh = pl.read_csv(MESH_PATH, infer_schema_length=10000)

    print("\nColunas Mesh:")
    print(mesh.columns)

    prices_by_listing = (
        prices
        .filter(pl.col("price").is_not_null() & (pl.col("price") > 0))
        .group_by("airbnb_listing_id")
        .agg(
            pl.mean("price").round(2).alias("avg_daily_price"),
            pl.median("price").round(2).alias("median_daily_price"),
            pl.min("price").alias("min_daily_price"),
            pl.max("price").alias("max_daily_price"),
            pl.len().alias("price_records"),
        )
    )

    details_prices = details.join(
        prices_by_listing,
        on="airbnb_listing_id",
        how="inner",
    )

    mesh_region = (
        mesh
        .select(
            [
                "airbnb_listing_id",
                "suburb",
            ]
        )
        .with_columns(
            pl.col("suburb")
            .cast(pl.Utf8)
            .map_elements(normalize_text, return_dtype=pl.Utf8)
            .alias("region")
        )
        .filter(pl.col("region").is_not_null())
        .unique(subset=["airbnb_listing_id"], keep="last")
    )

    df = details_prices.join(
        mesh_region,
        on="airbnb_listing_id",
        how="inner",
    )

    df = df.filter(
        pl.col("median_daily_price").is_not_null()
        & (pl.col("median_daily_price") > 0)
    )

    return (
        df
        .group_by("region")
        .agg(
            pl.len().alias("airbnb_listings"),
            pl.mean("avg_daily_price").round(2).alias("airbnb_avg_daily_price"),
            pl.median("median_daily_price").round(2).alias("airbnb_median_daily_price"),
            pl.mean("median_daily_price").round(2).alias("airbnb_mean_median_daily_price"),
        )
        .filter(pl.col("airbnb_listings") >= 10)
        .sort("airbnb_median_daily_price", descending=True)
    )


def load_vivareal_cost_by_region() -> pl.DataFrame:
    df = pl.read_csv(VIVAREAL_PATH, infer_schema_length=10000)

    df = df.with_columns(
        pl.col("sale_price")
        .map_elements(clean_money, return_dtype=pl.Float64)
        .alias("sale_price_clean"),
        pl.col("usable_area")
        .map_elements(clean_number, return_dtype=pl.Float64)
        .alias("area_m2"),
        pl.col("suburb")
        .cast(pl.Utf8)
        .map_elements(normalize_text, return_dtype=pl.Utf8)
        .alias("region"),
    )

    df = df.filter(
        pl.col("sale_price_clean").is_not_null()
        & pl.col("area_m2").is_not_null()
        & (pl.col("sale_price_clean") > 0)
        & (pl.col("area_m2") > 0)
    )

    df = df.with_columns(
        (pl.col("sale_price_clean") / pl.col("area_m2"))
        .round(2)
        .alias("price_per_m2")
    )

    df = df.filter(
        (pl.col("price_per_m2") >= 3000)
        & (pl.col("price_per_m2") <= 40000)
        & (pl.col("area_m2") >= 20)
        & (pl.col("area_m2") <= 500)
    )

    return (
        df
        .group_by("region")
        .agg(
            pl.len().alias("vivareal_listings"),
            pl.mean("sale_price_clean").round(2).alias("avg_sale_price"),
            pl.median("sale_price_clean").round(2).alias("median_sale_price"),
            pl.mean("area_m2").round(2).alias("avg_area_m2"),
            pl.median("area_m2").round(2).alias("median_area_m2"),
            pl.mean("price_per_m2").round(2).alias("avg_price_per_m2"),
            pl.median("price_per_m2").round(2).alias("median_price_per_m2"),
        )
        .filter(pl.col("vivareal_listings") >= 5)
    )


def calculate_roi_by_region(
    airbnb_summary: pl.DataFrame,
    vivareal_summary: pl.DataFrame,
) -> pl.DataFrame:
    base = airbnb_summary.join(
        vivareal_summary,
        on="region",
        how="inner",
    )

    rows = []

    for row in base.iter_rows(named=True):
        region = row["region"]
        daily_rate_2025 = row["airbnb_median_daily_price"]
        price_per_m2 = row["median_price_per_m2"]

        total_private_area = UNITS * UNIT_SIZE_M2
        estimated_capex = total_private_area * price_per_m2

        for year, growth in DAILY_RATE_GROWTH.items():
            projected_daily_rate = daily_rate_2025 * (1 + growth)

            gross_revenue = (
                UNITS
                * projected_daily_rate
                * 365
                * OCCUPANCY_RATE
            )

            operating_cost = gross_revenue * OPERATING_COST_RATE
            net_operating_income = gross_revenue - operating_cost

            roi_pct = (net_operating_income / estimated_capex) * 100
            payback_years = estimated_capex / net_operating_income

            rows.append(
                {
                    "region": region,
                    "year": year,
                    "airbnb_listings": row["airbnb_listings"],
                    "vivareal_listings": row["vivareal_listings"],
                    "airbnb_median_daily_price": round(daily_rate_2025, 2),
                    "projected_daily_rate": round(projected_daily_rate, 2),
                    "median_price_per_m2": round(price_per_m2, 2),
                    "units": UNITS,
                    "unit_size_m2": UNIT_SIZE_M2,
                    "total_private_area_m2": total_private_area,
                    "estimated_capex": round(estimated_capex, 2),
                    "gross_revenue": round(gross_revenue, 2),
                    "operating_cost": round(operating_cost, 2),
                    "net_operating_income": round(net_operating_income, 2),
                    "roi_pct": round(roi_pct, 2),
                    "payback_years": round(payback_years, 2),
                }
            )

    return (
        pl.DataFrame(rows)
        .sort(["year", "roi_pct"], descending=[False, True])
    )


def investment_ranking_2025(roi_df: pl.DataFrame) -> pl.DataFrame:
    return (
        roi_df
        .filter(pl.col("year") == 2025)
        .select(
            [
                "region",
                "airbnb_listings",
                "vivareal_listings",
                "airbnb_median_daily_price",
                "median_price_per_m2",
                "estimated_capex",
                "net_operating_income",
                "roi_pct",
                "payback_years",
            ]
        )
        .sort("roi_pct", descending=True)
    )


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    airbnb_summary = load_airbnb_region_revenue()
    vivareal_summary = load_vivareal_cost_by_region()

    roi_by_region = calculate_roi_by_region(
        airbnb_summary,
        vivareal_summary,
    )

    ranking_2025 = investment_ranking_2025(roi_by_region)

    print("\n" + "=" * 100)
    print("RECEITA AIRBNB POR REGIÃO")
    print("=" * 100)
    print(airbnb_summary)

    print("\n" + "=" * 100)
    print("CUSTO VIVAREAL POR REGIÃO")
    print("=" * 100)
    print(vivareal_summary.sort("median_price_per_m2"))

    print("\n" + "=" * 100)
    print("ROI POR REGIÃO - 2025 A 2027")
    print("=" * 100)
    print(roi_by_region)

    print("\n" + "=" * 100)
    print("RANKING DE INVESTIMENTO POR REGIÃO - 2025")
    print("=" * 100)
    print(ranking_2025)

    airbnb_summary.write_csv(OUTPUT_DIR / "airbnb_region_revenue_summary.csv")
    vivareal_summary.write_csv(OUTPUT_DIR / "vivareal_region_cost_summary.csv")
    roi_by_region.write_csv(OUTPUT_DIR / "roi_by_region_2025_2027.csv")
    ranking_2025.write_csv(OUTPUT_DIR / "investment_ranking_by_region_2025.csv")

    print("\nArquivos gerados:")
    print(OUTPUT_DIR / "airbnb_region_revenue_summary.csv")
    print(OUTPUT_DIR / "vivareal_region_cost_summary.csv")
    print(OUTPUT_DIR / "roi_by_region_2025_2027.csv")
    print(OUTPUT_DIR / "investment_ranking_by_region_2025.csv")


if __name__ == "__main__":
    main()