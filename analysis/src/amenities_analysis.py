from pathlib import Path
import re

import polars as pl
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error


DETAILS_PATH = Path("../data/Details_Itapema.csv")
PRICE_PATH = Path("../data/Price_AV_Itapema.csv")
OUTPUT_DIR = Path("output")


AMENITY_CATEGORIES = {
    "has_barbecue": ["churrasqueira", "churrasco"],
    "has_elevator": ["elevador"],
    "pet_friendly": ["permitido animais", "animais de estimação", "pet"],
    "has_parking": ["estacionamento", "garagem", "vaga"],
    "has_home_office": ["espaço de trabalho", "trabalho", "mesa"],
    "has_self_checkin": ["self check", "self", "check-in"],
    "long_term_allowed": ["estadias de longa duração", "longa duração"],
    "has_outdoor_area": ["varanda", "pátio", "área externa", "externa", "externo"],
    "has_security": ["extintor", "incêndio", "detector", "fumaça", "câmeras", "segurança"],
    "has_bathroom_items": ["secador de cabelo", "secador", "chuveiro", "água quente"],
    "has_laundry": ["máquina de lavar", "máquina", "lavar", "roupas", "secadora", "varal", "lavanderia"],
    "has_air_conditioning": ["ar-condicionado", "ar condicionado", "condicionado", "split"],
    "has_kitchen": ["cozinha", "fogão", "microondas", "refrigerador", "forno", "cafeteira", "liquidificador", "chaleira", "torradeira", "freezer", "louças", "talheres", "utensílios"],
}


def normalize_text(value: str) -> str:
    if value is None:
        return ""

    value = str(value).lower()

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

    value = re.sub(r"[\[\]{}\"']", " ", value)
    value = re.sub(r"[,;|/\\]", " ", value)
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def contains_any(text: str, keywords: list[str]) -> bool:
    text = normalize_text(text)
    return any(normalize_text(keyword) in text for keyword in keywords)


def clean_numeric_column(expr: pl.Expr) -> pl.Expr:
    return (
        expr.cast(pl.Utf8)
        .str.replace_all(r"[^0-9,.]", "")
        .str.replace_all(",", ".")
        .cast(pl.Float64, strict=False)
    )


def classify_beach_distance(description: str) -> str:
    text = normalize_text(description)

    if not text:
        return "05_sem_informacao"

    premium_terms = [
        "frente mar", "frente ao mar", "frente para o mar",
        "vista mar", "vista para o mar", "pe na areia",
        "beira mar", "beira-mar", "orla",
    ]

    if any(term in text for term in premium_terms):
        return "01_premium_frente_mar"

    high_proximity_terms = [
        "quadra mar", "quadra do mar", "quadras do mar",
        "uma quadra do mar", "1 quadra do mar",
        "a poucos metros da praia", "pertinho da praia",
    ]

    if any(term in text for term in high_proximity_terms):
        return "02_alta_proximidade_ate_200m"

    meter_patterns = [
        r"(\d{1,4})\s*(m|mts|metros)\s*(da|do|ate|a)?\s*(praia|mar)",
        r"(praia|mar)\s*(a|ate|em)?\s*(\d{1,4})\s*(m|mts|metros)",
        r"(\d{1,4})\s*(m|mts|metros)\s*da\s*meia\s*praia",
    ]

    for pattern in meter_patterns:
        match = re.search(pattern, text)
        if match:
            numbers = re.findall(r"\d{1,4}", match.group(0))
            if numbers:
                meters = int(numbers[0])

                if meters <= 200:
                    return "02_alta_proximidade_ate_200m"
                elif meters <= 500:
                    return "03_media_proximidade_201m_500m"
                else:
                    return "04_baixa_proximidade_acima_500m"

    minute_patterns = [
        r"(\d{1,2})\s*(min|minutos)\s*(da|do|ate|a)?\s*(praia|mar)",
        r"(praia|mar)\s*(a|em)?\s*(\d{1,2})\s*(min|minutos)",
    ]

    for pattern in minute_patterns:
        match = re.search(pattern, text)
        if match:
            numbers = re.findall(r"\d{1,2}", match.group(0))
            if numbers:
                minutes = int(numbers[0])

                if minutes <= 3:
                    return "02_alta_proximidade_ate_200m"
                elif minutes <= 7:
                    return "03_media_proximidade_201m_500m"
                else:
                    return "04_baixa_proximidade_acima_500m"

    generic_beach_terms = [
        "proximo a praia", "proximo da praia", "perto da praia",
        "caminhando ate a praia", "facil acesso a praia", "meia praia",
    ]

    if any(term in text for term in generic_beach_terms):
        return "03_media_proximidade_201m_500m"

    if "praia" in text or "mar" in text:
        return "03_media_proximidade_201m_500m"

    return "05_sem_informacao"


def load_data() -> pl.DataFrame:
    details = pl.read_csv(DETAILS_PATH, infer_schema_length=10000)
    prices = pl.read_csv(PRICE_PATH, infer_schema_length=10000)

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

    return details.join(
        prices_by_listing,
        on="airbnb_listing_id",
        how="inner",
    )


def add_amenity_flags(df: pl.DataFrame) -> pl.DataFrame:
    df = df.with_columns(
        pl.col("amenities")
        .cast(pl.Utf8)
        .map_elements(normalize_text, return_dtype=pl.Utf8)
        .alias("amenities_text")
    )

    for category, keywords in AMENITY_CATEGORIES.items():
        df = df.with_columns(
            pl.col("amenities_text")
            .map_elements(
                lambda text, kw=keywords: contains_any(text, kw),
                return_dtype=pl.Boolean,
            )
            .alias(category)
        )

    amenity_cols = list(AMENITY_CATEGORIES.keys())

    return df.with_columns(
        sum(pl.col(col).cast(pl.Int64) for col in amenity_cols)
        .alias("amenity_score")
    )


def add_beach_distance_category(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(
        pl.col("ad_description")
        .cast(pl.Utf8)
        .map_elements(classify_beach_distance, return_dtype=pl.Utf8)
        .alias("beach_distance_category")
    )


def add_property_features(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df
        .with_columns(
            clean_numeric_column(pl.col("number_of_bathrooms")).alias("bathrooms"),
            clean_numeric_column(pl.col("number_of_bedrooms")).alias("bedrooms"),
            clean_numeric_column(pl.col("number_of_beds")).alias("beds"),
            clean_numeric_column(pl.col("number_of_guests")).alias("accommodates"),
        )
        .with_columns(
            (pl.col("median_daily_price") / pl.col("accommodates"))
            .round(2)
            .alias("price_per_guest"),
            (pl.col("median_daily_price") / pl.col("bedrooms"))
            .round(2)
            .alias("price_per_bedroom"),
            (pl.col("median_daily_price") / pl.col("bathrooms"))
            .round(2)
            .alias("price_per_bathroom"),
        )
    )


def add_price_segments(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(
        pl.when(pl.col("median_daily_price") >= 800)
        .then(pl.lit("04_premium_800_plus"))
        .when(pl.col("median_daily_price") >= 600)
        .then(pl.lit("03_high_600_799"))
        .when(pl.col("median_daily_price") >= 400)
        .then(pl.lit("02_mid_400_599"))
        .otherwise(pl.lit("01_low_below_400"))
        .alias("price_segment")
    )


def capacity_analysis(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df
        .filter(
            pl.col("accommodates").is_not_null()
            & (pl.col("accommodates") > 0)
            & (pl.col("accommodates") <= 20)
        )
        .group_by("accommodates")
        .agg(
            pl.len().alias("listings"),
            pl.mean("median_daily_price").round(2).alias("avg_daily_price"),
            pl.median("median_daily_price").round(2).alias("median_daily_price"),
            pl.mean("price_per_guest").round(2).alias("avg_price_per_guest"),
            pl.median("price_per_guest").round(2).alias("median_price_per_guest"),
            pl.mean("amenity_score").round(2).alias("avg_amenity_score"),
        )
        .filter(pl.col("listings") >= 10)
        .sort("accommodates")
    )


def bedroom_analysis(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df
        .filter(
            pl.col("bedrooms").is_not_null()
            & (pl.col("bedrooms") > 0)
            & (pl.col("bedrooms") <= 10)
        )
        .group_by("bedrooms")
        .agg(
            pl.len().alias("listings"),
            pl.mean("median_daily_price").round(2).alias("avg_daily_price"),
            pl.median("median_daily_price").round(2).alias("median_daily_price"),
            pl.mean("price_per_bedroom").round(2).alias("avg_price_per_bedroom"),
            pl.median("price_per_bedroom").round(2).alias("median_price_per_bedroom"),
            pl.mean("price_per_guest").round(2).alias("avg_price_per_guest"),
            pl.median("price_per_guest").round(2).alias("median_price_per_guest"),
        )
        .filter(pl.col("listings") >= 10)
        .sort("bedrooms")
    )


def property_configuration_analysis(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df
        .filter(
            pl.col("accommodates").is_not_null()
            & pl.col("bedrooms").is_not_null()
            & pl.col("bathrooms").is_not_null()
            & (pl.col("accommodates") > 0)
            & (pl.col("bedrooms") > 0)
            & (pl.col("bathrooms") > 0)
        )
        .group_by(["accommodates", "bedrooms", "bathrooms"])
        .agg(
            pl.len().alias("listings"),
            pl.median("median_daily_price").round(2).alias("median_daily_price"),
            pl.mean("median_daily_price").round(2).alias("avg_daily_price"),
            pl.median("price_per_guest").round(2).alias("median_price_per_guest"),
            pl.mean("price_per_guest").round(2).alias("avg_price_per_guest"),
            pl.mean("amenity_score").round(2).alias("avg_amenity_score"),
            pl.mean("has_barbecue").round(2).alias("barbecue_rate"),
            pl.mean("has_elevator").round(2).alias("elevator_rate"),
            pl.mean("pet_friendly").round(2).alias("pet_friendly_rate"),
        )
        .filter(pl.col("listings") >= 10)
        .sort(["median_daily_price"], descending=True)
    )


def best_return_configurations(df: pl.DataFrame) -> pl.DataFrame:
    return (
        property_configuration_analysis(df)
        .with_columns(
            (
                pl.col("median_daily_price")
                / pl.col("median_price_per_guest")
            )
            .round(2)
            .alias("value_efficiency_index")
        )
        .sort(
            ["median_daily_price", "median_price_per_guest"],
            descending=[True, False],
        )
    )


def beach_distance_summary(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df
        .group_by("beach_distance_category")
        .agg(
            pl.len().alias("listings"),
            pl.mean("amenity_score").round(2).alias("avg_amenity_score"),
            pl.median("amenity_score").alias("median_amenity_score"),
            pl.mean("avg_daily_price").round(2).alias("avg_daily_price"),
            pl.median("median_daily_price").round(2).alias("median_daily_price"),
        )
        .sort("beach_distance_category")
    )


def amenity_impact_by_beach_distance(
    df: pl.DataFrame,
    min_group_size: int = 20,
) -> pl.DataFrame:
    rows = []

    distance_categories = (
        df
        .filter(pl.col("beach_distance_category").is_not_null())
        .select("beach_distance_category")
        .unique()
        .sort("beach_distance_category")
        .to_series()
        .to_list()
    )

    for distance_category in distance_categories:
        subset = df.filter(pl.col("beach_distance_category") == distance_category)

        for amenity in AMENITY_CATEGORIES.keys():
            with_amenity = subset.filter(pl.col(amenity))
            without_amenity = subset.filter(~pl.col(amenity))

            if with_amenity.height < min_group_size or without_amenity.height < min_group_size:
                continue

            median_with = with_amenity.select(pl.median("median_daily_price")).item()
            median_without = without_amenity.select(pl.median("median_daily_price")).item()

            avg_with = with_amenity.select(pl.mean("avg_daily_price")).item()
            avg_without = without_amenity.select(pl.mean("avg_daily_price")).item()

            rows.append(
                {
                    "beach_distance_category": distance_category,
                    "amenity": amenity,
                    "listings_with": with_amenity.height,
                    "listings_without": without_amenity.height,
                    "median_with": round(median_with, 2),
                    "median_without": round(median_without, 2),
                    "median_diff": round(median_with - median_without, 2),
                    "premium_pct": round(
                        ((median_with - median_without) / median_without) * 100,
                        2,
                    )
                    if median_without
                    else None,
                    "avg_with": round(avg_with, 2),
                    "avg_without": round(avg_without, 2),
                    "avg_diff": round(avg_with - avg_without, 2),
                }
            )

    if not rows:
        return pl.DataFrame()

    return (
        pl.DataFrame(rows)
        .sort(
            ["beach_distance_category", "premium_pct"],
            descending=[False, True],
        )
    )


def estimate_marginal_effects(df: pl.DataFrame) -> pl.DataFrame:
    impact = amenity_impact_by_beach_distance(df, min_group_size=20)

    if impact.is_empty():
        return impact

    return (
        impact
        .with_columns(
            (pl.col("listings_with") + pl.col("listings_without"))
            .alias("comparable_listings")
        )
        .group_by("amenity")
        .agg(
            pl.sum("comparable_listings").alias("total_comparable_listings"),
            (
                (pl.col("premium_pct") * pl.col("comparable_listings")).sum()
                / pl.col("comparable_listings").sum()
            )
            .round(2)
            .alias("weighted_premium_pct"),
            (
                (pl.col("median_diff") * pl.col("comparable_listings")).sum()
                / pl.col("comparable_listings").sum()
            )
            .round(2)
            .alias("weighted_median_diff"),
            pl.len().alias("distance_categories_used"),
        )
        .sort("weighted_premium_pct", descending=True)
    )


def prepare_model_df(df: pl.DataFrame) -> pd.DataFrame:
    model_df = df.select(
        [
            "median_daily_price",
            "accommodates",
            "bedrooms",
            "bathrooms",
            "beds",
            "amenity_score",
            "has_barbecue",
            "has_elevator",
            "pet_friendly",
            "has_parking",
            "beach_distance_category",
        ]
    ).to_pandas()

    model_df["front_beach"] = (
        model_df["beach_distance_category"] == "01_premium_frente_mar"
    ).astype(int)

    bool_cols = [
        "has_barbecue",
        "has_elevator",
        "pet_friendly",
        "has_parking",
    ]

    for col in bool_cols:
        model_df[col] = model_df[col].astype(int)

    numeric_cols = [
        "median_daily_price",
        "accommodates",
        "bedrooms",
        "bathrooms",
        "beds",
        "amenity_score",
    ]

    for col in numeric_cols:
        model_df[col] = pd.to_numeric(model_df[col], errors="coerce")

    model_df = model_df.dropna()
    model_df = model_df[
        (model_df["median_daily_price"] > 0)
        & (model_df["accommodates"] > 0)
        & (model_df["bedrooms"] > 0)
        & (model_df["bathrooms"] > 0)
    ]

    return model_df


def run_linear_regression(df: pl.DataFrame):
    model_df = prepare_model_df(df)

    features = [
        "front_beach",
        "has_barbecue",
        "has_elevator",
        "pet_friendly",
        "has_parking",
        "accommodates",
        "bedrooms",
        "bathrooms",
        "beds",
    ]

    X = model_df[features]
    y = model_df["median_daily_price"]

    model = LinearRegression()
    model.fit(X, y)

    predictions = model.predict(X)

    coef_df = (
        pd.DataFrame(
            {
                "feature": features,
                "estimated_price_impact_brl": model.coef_,
            }
        )
        .round(2)
        .sort_values("estimated_price_impact_brl", ascending=False)
    )

    metrics_df = pd.DataFrame(
        [
            {
                "model": "linear_regression",
                "rows_used": len(model_df),
                "r2_score": round(r2_score(y, predictions), 4),
                "mae_brl": round(mean_absolute_error(y, predictions), 2),
                "intercept_brl": round(float(model.intercept_), 2),
            }
        ]
    )

    return pl.from_pandas(coef_df), pl.from_pandas(metrics_df)


def run_random_forest(df: pl.DataFrame):
    model_df = prepare_model_df(df)

    features = [
        "front_beach",
        "has_barbecue",
        "has_elevator",
        "pet_friendly",
        "has_parking",
        "accommodates",
        "bedrooms",
        "bathrooms",
        "beds",
    ]

    X = model_df[features]
    y = model_df["median_daily_price"]

    model = RandomForestRegressor(
        n_estimators=500,
        max_depth=8,
        random_state=42,
    )

    model.fit(X, y)

    predictions = model.predict(X)

    importance_df = (
        pd.DataFrame(
            {
                "feature": features,
                "importance": model.feature_importances_,
            }
        )
        .sort_values("importance", ascending=False)
    )

    metrics_df = pd.DataFrame(
        [
            {
                "model": "random_forest",
                "rows_used": len(model_df),
                "r2_score": round(r2_score(y, predictions), 4),
                "mae_brl": round(mean_absolute_error(y, predictions), 2),
            }
        ]
    )

    return pl.from_pandas(importance_df), pl.from_pandas(metrics_df)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = load_data()
    df = add_amenity_flags(df)
    df = add_beach_distance_category(df)
    df = add_property_features(df)
    df = add_price_segments(df)

    distance_summary = beach_distance_summary(df)
    capacity_summary = capacity_analysis(df)
    bedroom_summary = bedroom_analysis(df)
    configuration_summary = property_configuration_analysis(df)
    best_configs = best_return_configurations(df)
    impact_by_distance = amenity_impact_by_beach_distance(df, min_group_size=20)
    marginal_effects = estimate_marginal_effects(df)
    linear_coef, linear_metrics = run_linear_regression(df)
    rf_importance, rf_metrics = run_random_forest(df)

    print("\n" + "=" * 100)
    print("RESUMO POR PROXIMIDADE DA PRAIA")
    print("=" * 100)
    print(distance_summary)

    print("\n" + "=" * 100)
    print("ANÁLISE POR CAPACIDADE DE HÓSPEDES")
    print("=" * 100)
    print(capacity_summary)

    print("\n" + "=" * 100)
    print("ANÁLISE POR QUANTIDADE DE QUARTOS")
    print("=" * 100)
    print(bedroom_summary)

    print("\n" + "=" * 100)
    print("MELHORES CONFIGURAÇÕES DO IMÓVEL")
    print("=" * 100)
    print(configuration_summary)

    print("\n" + "=" * 100)
    print("CONFIGURAÇÕES COM MELHOR RETORNO")
    print("=" * 100)
    print(best_configs)

    print("\n" + "=" * 100)
    print("IMPACTO MARGINAL DAS AMENITIES CONTROLANDO POR PROXIMIDADE")
    print("=" * 100)
    print(marginal_effects)

    print("\n" + "=" * 100)
    print("REGRESSÃO LINEAR - IMPACTO ESTIMADO NO PREÇO DA DIÁRIA")
    print("=" * 100)
    print(linear_coef)

    print("\n" + "=" * 100)
    print("MÉTRICAS REGRESSÃO LINEAR")
    print("=" * 100)
    print(linear_metrics)

    print("\n" + "=" * 100)
    print("RANDOM FOREST - FEATURE IMPORTANCE")
    print("=" * 100)
    print(rf_importance)

    print("\n" + "=" * 100)
    print("MÉTRICAS RANDOM FOREST")
    print("=" * 100)
    print(rf_metrics)

    df.write_csv(OUTPUT_DIR / "listings_enriched_full.csv")
    distance_summary.write_csv(OUTPUT_DIR / "beach_distance_summary.csv")
    capacity_summary.write_csv(OUTPUT_DIR / "capacity_analysis.csv")
    bedroom_summary.write_csv(OUTPUT_DIR / "bedroom_analysis.csv")
    configuration_summary.write_csv(OUTPUT_DIR / "property_configuration_analysis.csv")
    best_configs.write_csv(OUTPUT_DIR / "best_return_configurations.csv")
    impact_by_distance.write_csv(OUTPUT_DIR / "amenity_impact_by_beach_distance.csv")
    marginal_effects.write_csv(OUTPUT_DIR / "amenity_marginal_effects_controlled_by_distance.csv")
    linear_coef.write_csv(OUTPUT_DIR / "linear_regression_coefficients.csv")
    linear_metrics.write_csv(OUTPUT_DIR / "linear_regression_metrics.csv")
    rf_importance.write_csv(OUTPUT_DIR / "random_forest_feature_importance.csv")
    rf_metrics.write_csv(OUTPUT_DIR / "random_forest_metrics.csv")

    print("\nArquivos gerados em output/")


if __name__ == "__main__":
    main()