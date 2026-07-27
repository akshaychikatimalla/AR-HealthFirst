import pandas as pd

df = pd.read_csv("drug_interactions.csv")

def normalize(name: str) -> str:
    if not name:
        return ""
    return name.lower().strip().split()[0]

def check_interactions(compositions: list, current_medicines: list) -> list:
    """
    compositions: list of active ingredients from scanned medicine
    current_medicines: list of medicines patient currently takes
    """
    if not compositions:
        return []

    results = []
    seen = set()  # avoid duplicate results

    for ingredient in compositions:
        ing_norm = normalize(ingredient)

        for current in current_medicines:
            current_norm = normalize(current)

            match = df[
                ((df["drug_a"].str.lower() == ing_norm) &
                 (df["drug_b"].str.lower() == current_norm)) |
                ((df["drug_a"].str.lower() == current_norm) &
                 (df["drug_b"].str.lower() == ing_norm))
            ]

            if not match.empty:
                for _, row in match.iterrows():
                    key = f"{row['drug_a']}-{row['drug_b']}"
                    if key not in seen:
                        seen.add(key)
                        results.append({
                            "ingredient": ing_norm,
                            "conflicts_with": current_norm,
                            "severity": row["severity"],
                            "description": row["description"]
                        })

    return results