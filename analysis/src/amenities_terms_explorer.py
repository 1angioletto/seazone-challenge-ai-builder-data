import re
from collections import Counter
from pathlib import Path

import polars as pl

DATA_PATH = Path("../data")

details = pl.read_csv(DATA_PATH / "Details_Itapema.csv")

texts = (
    details
    .select("amenities")
    .with_columns(
        pl.col("amenities")
        .cast(pl.Utf8)
        .fill_null("")
        .str.to_lowercase()
    )
    .to_series()
    .to_list()
)

stopwords = {
    "de", "da", "do", "das", "dos", "e", "em", "com", "para", "por",
    "a", "o", "as", "os", "um", "uma", "no", "na", "nos", "nas",
    "the", "and", "with", "for", "in", "of", "to", "is", "on",
    "available", "included", "provided", "basic", "free"
}

counter = Counter()

for text in texts:
    tokens = re.findall(r"[a-záéíóúâêîôûãõç]+", text)

    tokens = [
        token for token in tokens
        if len(token) >= 3 and token not in stopwords
    ]

    counter.update(tokens)

print("\nTop 100 termos mais frequentes em amenities")
for term, count in counter.most_common(100):
    print(f"{term}: {count}")