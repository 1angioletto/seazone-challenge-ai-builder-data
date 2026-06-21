from pathlib import Path
import re
import polars as pl


VIVAREAL_PATH = Path("../data/VivaReal_Itapema.csv")
OUTPUT_DIR = Path("output")

# Premissas do prédio
UNITS = 50
UNIT_SIZE_M2 = 100
TARGET_DAILY_RATE_2025 = 700  # diária mediana aproximada do perfil 8 hóspedes / 3 quartos
OCCUPANCY_RATE = 0.62         # ocupação anual estimada
OPERATING_COST_RATE = 0.35    # custo operacional sobre receita bruta

# Projeções anuais
DAILY_RATE_GROWTH = {
    2025: 0.00,
    2026: 0.08,
    2027: 0.16,
}


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


def find_column(df: pl.DataFrame, candidates: list[str]) -> str:
    for col in candidates:
        if col in df.columns:
            return col

    raise ValueError(
        f"Nenhuma coluna encontrada entre {candidates}. "
        f"Colunas disponíveis: {df.columns}"
    )


def load_vivareal() -> pl.DataFrame:
    df = pl.read_csv(VIVAREAL_PATH, infer_schema_length=10000)

    print("\nColunas encontradas no VivaReal:")
    print(df.columns)

    price_col = find_column(
        df,
        [
            "price",
            "preco",
            "valor",
            "sale_price",
            "listing_price",
            "Preço",
            "Valor",
        ],
    )

    area_col = find_column(
        df,
        [
            "area",
            "area_m2",
            "usable_area",
            "total_area",
            "area_total",
            "Área",
            "Area",
        ],
    )

    location_col = find_column(
        df,
        [
            "suburb",
            "bairro",
            "neighborhood",
            "location",
            "address",
            "endereco",
            "localizacao",
        ],
    )

    df = df.with_columns(
        pl.col(price_col)
        .map_elements(clean_money, return_dtype=pl.Float64)
        .alias("sale_price"),
        pl.col(area_col)
        .map_elements(clean_number, return_dtype=pl.Float64)
        .alias("area_m2"),
        pl.col(location_col)
        .cast(pl.Utf8)
        .str.to_lowercase()
        .alias("region"),
    )

    df = df.filter(
        pl.col("sale_price").is_not_null()
        & pl.col("area_m2").is_not_null()
        & (pl.col("sale_price") > 0)
        & (pl.col("area_m2") > 0)
    )

    df = df.with_columns(
        (pl.col("sale_price") / pl.col("area_m2"))
        .round(2)
        .alias("price_per_m2")
    )

    # Remove outliers absurdos
    df = df.filter(
        (pl.col("price_per_m2") >= 3000)
        & (pl.col("price_per_m2") <= 40000)
        & (pl.col("area_m2") >= 20)
        & (pl.col("area_m2") <= 500)
    )

    return df


def vivareal_region_summary(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df.group_by("region")
        .agg(
            pl.len().alias("listings"),
            pl.mean("sale_price").round(2).alias("avg_sale_price"),
            pl.median("sale_price").round(2).alias("median_sale_price"),
            pl.mean("area_m2").round(2).alias("avg_area_m2"),
            pl.median("area_m2").round(2).alias("median_area_m2"),
            pl.mean("price_per_m2").round(2).alias("avg_price_per_m2"),
            pl.median("price_per_m2").round(2).alias("median_price_per_m2"),
        )
        .filter(pl.col("listings") >= 5)
        .sort("median_price_per_m2")
    )


def project_roi(region_summary: pl.DataFrame) -> pl.DataFrame:
    rows = []

    for row in region_summary.iter_rows(named=True):
        region = row["region"]
        price_per_m2 = row["median_price_per_m2"]

        total_private_area = UNITS * UNIT_SIZE_M2
        estimated_capex = total_private_area * price_per_m2

        for year, growth in DAILY_RATE_GROWTH.items():
            projected_daily_rate = TARGET_DAILY_RATE_2025 * (1 + growth)

            gross_revenue = (
                UNITS
                * projected_daily_rate
                * 365
                * OCCUPANCY_RATE
            )

            operating_cost = gross_revenue * OPERATING_COST_RATE
            net_operating_income = gross_revenue - operating_cost

            roi = net_operating_income / estimated_capex

            rows.append(
                {
                    "region": region,
                    "year": year,
                    "units": UNITS,
                    "unit_size_m2": UNIT_SIZE_M2,
                    "total_private_area_m2": total_private_area,
                    "median_price_per_m2": round(price_per_m2, 2),
                    "estimated_capex": round(estimated_capex, 2),
                    "projected_daily_rate": round(projected_daily_rate, 2),
                    "occupancy_rate": OCCUPANCY_RATE,
                    "gross_revenue": round(gross_revenue, 2),
                    "operating_cost": round(operating_cost, 2),
                    "net_operating_income": round(net_operating_income, 2),
                    "roi_pct": round(roi * 100, 2),
                    "payback_years": round(estimated_capex / net_operating_income, 2),
                }
            )

    return pl.DataFrame(rows).sort(["year", "roi_pct"], descending=[False, True])


def best_regions_for_investment(roi_df: pl.DataFrame) -> pl.DataFrame:
    return (
        roi_df.filter(pl.col("year") == 2025)
        .select(
            [
                "region",
                "median_price_per_m2",
                "estimated_capex",
                "projected_daily_rate",
                "net_operating_income",
                "roi_pct",
                "payback_years",
            ]
        )
        .sort("roi_pct", descending=True)
    )


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    vivareal = load_vivareal()
    region_summary = vivareal_region_summary(vivareal)
    roi_projection = project_roi(region_summary)
    best_regions = best_regions_for_investment(roi_projection)

    print("\n" + "=" * 100)
    print("RESUMO VIVAREAL POR REGIÃO")
    print("=" * 100)
    print(region_summary)

    print("\n" + "=" * 100)
    print("PROJEÇÃO DE ROI - PRÉDIO COM 50 APARTAMENTOS")
    print("=" * 100)
    print(roi_projection)

    print("\n" + "=" * 100)
    print("MELHORES REGIÕES PARA INVESTIMENTO - 2025")
    print("=" * 100)
    print(best_regions)

    vivareal.write_csv(OUTPUT_DIR / "vivareal_cleaned.csv")
    region_summary.write_csv(OUTPUT_DIR / "vivareal_region_summary.csv")
    roi_projection.write_csv(OUTPUT_DIR / "building_roi_projection_2025_2027.csv")
    best_regions.write_csv(OUTPUT_DIR / "best_regions_for_investment.csv")

    print("\nArquivos gerados:")
    print(OUTPUT_DIR / "vivareal_cleaned.csv")
    print(OUTPUT_DIR / "vivareal_region_summary.csv")
    print(OUTPUT_DIR / "building_roi_projection_2025_2027.csv")
    print(OUTPUT_DIR / "best_regions_for_investment.csv")


if __name__ == "__main__":
    main()