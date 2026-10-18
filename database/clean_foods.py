import pandas as pd

RAW_FILE = "data/raw/food1.csv"
OUT_FILE = "data/foods_clean.csv"

# Kaggle column name -> our foods table column name
COLUMNS = {
    "Description": "name",
    "Data.Kilocalories": "calories_per_100g",
    "Data.Protein": "protein_g",
    "Data.Carbohydrate": "carbs_g",
    "Data.Fat.Total Lipid": "fat_g",
}


def build_clean_foods():
    # 1. read only the 5 columns we need (the file has 48)
    raw = pd.read_csv(RAW_FILE, usecols=list(COLUMNS))
    foods = raw.rename(columns=COLUMNS)[list(COLUMNS.values())]

    # 2. tidy the names: "EGG,WHOLE,RAW,FRESH" -> "Egg, whole, raw, fresh"
    foods["name"] = (
        foods["name"]
        .str.replace(r"\s+", " ", regex=True)       # squash repeated spaces
        .str.strip()
        .str.capitalize()
        .str.replace(r",\s*", ", ", regex=True)     # one space after each comma
    )

    # 3. drop rows that are missing a value
    foods = foods.dropna()

    # 4. remove duplicates: exact copies first, then repeated names
    #    (the dataset cuts names off at 60 characters, so two different
    #    products can end up with the same name; we keep the first)
    foods = foods.drop_duplicates()
    foods = foods.drop_duplicates(subset="name", keep="first")

    # 5. sort so the output is the same every run
    return foods.sort_values("name").reset_index(drop=True)


if __name__ == "__main__":
    foods = build_clean_foods()
    foods.to_csv(OUT_FILE, index=False)
    print(f"Wrote {len(foods)} foods to {OUT_FILE}")
    print(foods.head())