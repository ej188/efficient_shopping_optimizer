from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, List
import pandas as pd
import numpy as np
import json

# Resolve paths relative to the project root (one level above src/)
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
CLEAN_CSV = DATA_DIR / "eso_new_ver1.csv"
PARAMS_PATH = DATA_DIR / "params.json"

__all__ = [
    "BasketParams",
    "locate_clean_csv",
    "load_catalog",
    "value_per_dollar",
    "build_basket",
    "save_params",
    "load_params",
]

@dataclass
class BasketParams:
    budget: float = 40.0
    max_items: int = 15
    include_categories: Optional[List[str]] = None
    include_classes: Optional[List[str]] = None
    wP: float = 1.0
    wFi: float = 0.3
    wC: float = 0.1
    wF: float = 0.2
    tProtein: float = 0
    tFiber: float = 0
    tFatMax: float = 999
    tCarbMax: float = 999
    allow_multiples: bool = False
    max_qty_per_item: int = 1

def locate_clean_csv() -> Path:
    """Return the default catalog CSV path. Raises if missing."""
    if CLEAN_CSV.exists():
        return CLEAN_CSV
    raise FileNotFoundError(
        f"Missing {CLEAN_CSV} — expected the main catalog at data/eso_new_ver1.csv."
    )

def load_catalog(csv_path: Optional[Path] = None) -> pd.DataFrame:
    path = Path(csv_path) if csv_path else locate_clean_csv()
    if not Path(path).exists():
        raise FileNotFoundError(f"Catalog not found at {path}.")
    df = pd.read_csv(path)
    # drop spurious unnamed columns
    df = df.loc[:, ~df.columns.str.match(r'^Unnamed')]
    # light, idempotent cleaning for eso_new_ver1.csv schema
    for c in ["calories_per_100g","protein_per_100g","fat_per_100g","carbs_per_100g","fiber_per_100g","price_per_100g"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["item_name","category","classification","price_per_100g"]).copy()
    df["price_per_100g"] = df["price_per_100g"].clip(lower=0)
    for c in ["protein_per_100g","fat_per_100g","carbs_per_100g","fiber_per_100g","calories_per_100g"]:
        df[c] = df[c].fillna(0)
    return df

def value_per_dollar(frame, wP, wFi, wC, wF):
    numer = (wP*frame["protein_per_100g"] + wFi*frame["fiber_per_100g"]
             - wC*frame["carbs_per_100g"] - wF*frame["fat_per_100g"])
    denom = frame["price_per_100g"].replace(0, np.nan)
    return (numer/denom).fillna(-1e9)

def build_basket(df: pd.DataFrame, params: BasketParams) -> tuple[pd.DataFrame, dict]:
    """Greedy picker that can buy multiple 100g units per item (controlled by params).
    Returns (basket_df, summary_dict)."""
    frame = df.copy()
    if params.include_categories:
        frame = frame[frame["category"].isin(params.include_categories)]
    if params.include_classes:
        frame = frame[frame["classification"].isin(params.include_classes)]
    if frame.empty:
        return pd.DataFrame(), {"items": 0, "spent_$": 0}

    frame["value_per_dollar"] = value_per_dollar(frame, params.wP, params.wFi, params.wC, params.wF)
    frame = frame.sort_values(["value_per_dollar","price_per_100g"], ascending=[False, True])

    basket, spent = [], 0.0
    totals = dict(protein=0.0,fiber=0.0,fat=0.0,carbs=0.0,calories=0.0)
    for _, r in frame.iterrows():
        # Stop if we've reached the distinct-item cap
        if len(basket) >= params.max_items:
            break

        p = r["price_per_100g"]
        if p <= 0:
            continue

        # How many 100g units of this item we are allowed to buy
        unit_cap = params.max_qty_per_item if params.allow_multiples else 1

        # We'll aggregate multiples into a single line by increasing qty_100g
        qty = 0
        line = None

        # Try to add up to `unit_cap` units while staying within budget and soft caps
        while (
            qty < unit_cap
            and len(basket) <= params.max_items  # allow adding this item as the last slot
            and spent + p <= params.budget
        ):
            # Tentative totals if we add one more 100g unit
            new_totals = {
                "protein": totals["protein"] + r["protein_per_100g"],
                "fiber":   totals["fiber"]   + r["fiber_per_100g"],
                "fat":     totals["fat"]     + r["fat_per_100g"],
                "carbs":   totals["carbs"]   + r["carbs_per_100g"],
                "calories":totals["calories"]+ r["calories_per_100g"],
            }

            # Soft guardrails near fat/carb caps
            if (
                params.tFatMax < 900
                and new_totals["fat"] > 0.9 * params.tFatMax
                and r["fat_per_100g"] > r["protein_per_100g"]
            ):
                break
            if (
                params.tCarbMax < 900
                and new_totals["carbs"] > 0.9 * params.tCarbMax
                and r["carbs_per_100g"] > 2 * (1 + r["fiber_per_100g"])
            ):
                break

            # Commit this unit
            qty += 1
            totals = new_totals
            spent += p

            if line is None:
                line = {
                    "item_name": r["item_name"],
                    "category": r["category"],
                    "classification": r["classification"],
                    "qty_100g": 1,
                    "line_cost_$": round(p, 2),
                    "protein_g": r["protein_per_100g"],
                    "fiber_g": r["fiber_per_100g"],
                    "fat_g": r["fat_per_100g"],
                    "carbs_g": r["carbs_per_100g"],
                    "calories_kcal": r["calories_per_100g"],
                }
                basket.append(line)
            else:
                # Update the existing line to reflect another 100g unit
                line["qty_100g"] += 1
                line["line_cost_$"] = round(line["line_cost_$"] + p, 2)
                line["protein_g"] += r["protein_per_100g"]
                line["fiber_g"] += r["fiber_per_100g"]
                line["fat_g"] += r["fat_per_100g"]
                line["carbs_g"] += r["carbs_per_100g"]
                line["calories_kcal"] += r["calories_per_100g"]

    summary = {
        "items": len(basket),
        "spent_$": round(spent,2),
        "protein_g": round(totals["protein"],1),
        "fiber_g": round(totals["fiber"],1),
        "fat_g": round(totals["fat"],1),
        "carbs_g": round(totals["carbs"],1),
        "calories_kcal": round(totals["calories"],0),
    }
    return pd.DataFrame(basket), summary

def save_params(params: BasketParams):
    PARAMS_PATH.write_text(json.dumps(asdict(params), indent=2))

def load_params():
    if PARAMS_PATH.exists():
        return json.loads(PARAMS_PATH.read_text())
    return None