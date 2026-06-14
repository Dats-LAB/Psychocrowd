"""Transforms AI confidence probabilities into per-profile success probabilities."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from config import PROFILES


DIFFICULTY_FACTORS = {
    "easy":   1.10,
    "medium": 1.00,
    "hard":   0.75,
}


def transform_probability(p_base: float, profile: str, difficulty: str = "medium") -> float:
    """
    P_profil = clip(P_IA + delta_profil * coeff_difficulte, 0.05, 0.99)
    Coefficients : easy=1.10 | medium=1.00 | hard=0.75
    """
    delta = PROFILES.get(profile, 0.0)
    coeff = {"easy": 1.10, "medium": 1.00, "hard": 0.75}.get(difficulty, 1.00)
    return float(np.clip(p_base + delta * coeff, 0.05, 0.99))


def build_probability_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Compute success probability for each profile for every item."""
    # Ensure item_id exists
    if 'item_id' not in df.columns:
        df = df.copy()
        df.insert(0, 'item_id', range(len(df)))
    
    rows = []
    for idx, item in df.iterrows():
        p_base = item["ai_confidence"]
        difficulty = item.get("difficulty_expert", "medium")
        row = {
            "item_id": item["item_id"],
            "difficulty": difficulty,
            "p_base": p_base,
        }
        for profile in PROFILES:
            row[f"p_{profile}"] = transform_probability(p_base, profile, difficulty)
        rows.append(row)
    return pd.DataFrame(rows)



def print_profile_summary(matrix_df: pd.DataFrame):
    """Print formatted table of mean success rate per profile per difficulty."""
    profiles = list(PROFILES.keys())
    difficulties = ["easy", "medium", "hard"]

    print("\n  Profile Performance Matrix (mean P_correct):")
    print("  " + "-" * 45)
    header = f"  {'Profile':<10}"
    for d in difficulties:
        header += f"| {d.capitalize():<8}"
    print(header)
    print("  " + "-" * 45)

    for profile in profiles:
        line = f"  {profile.capitalize():<10}"
        for diff in difficulties:
            mask = matrix_df["difficulty"] == diff
            mean_p = matrix_df.loc[mask, f"p_{profile}"].mean()
            line += f"| {mean_p:<8.3f}"
        print(line)
    print("  " + "-" * 45 + "\n")
