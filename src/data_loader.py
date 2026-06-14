"""Handles loading real MCQ data and human response data with automatic fallback to mock data."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import warnings
from pathlib import Path
from config import MOCK_N_ITEMS, MOCK_N_HUMANS, MOCK_RANDOM_SEED

FIRST_NAMES = ["Emma", "Hugo", "Jade", "Raphael", "Louise", "Leo", "Alice", "Louis", "Lina", "Gabriel", "Chloe", "Arthur", "Mila", "Jules", "Lea", "Mael", "Manon", "Lucas", "Rose", "Adam"]
LAST_NAMES = ["Martin", "Bernard", "Thomas", "Petit", "Robert", "Richard", "Durand", "Dubois", "Moreau", "Laurent", "Simon", "Michel", "Lefebvre", "Leroy", "Roux", "David", "Bertrand", "Morel", "Fournier", "Girard"]


REQUIRED_MCQ_COLS = [
    "question", "option_a", "option_b", "option_c", "option_d",
    "correct_option", "difficulty_expert"
]
REQUIRED_HUMAN_COLS = ["student_id", "item_id", "response"]


def classify_domain(question: str) -> str:
    """Classify mathematical question into a domain based on keywords."""
    q_lower = str(question).lower()
    if "lim_" in q_lower or "d/dx" in q_lower or "limit" in q_lower or "derivative" in q_lower or "integrate" in q_lower or "integral" in q_lower:
        return "Calculus"
    elif "z =" in q_lower or "|z|" in q_lower or "complex" in q_lower or "1i" in q_lower or "conjugate" in q_lower:
        return "Complex Numbers"
    elif "x^2" in q_lower or "factorize" in q_lower or "expand" in q_lower or "solve" in q_lower or "equation" in q_lower:
        return "Algebra & Polynomials"
    elif "area" in q_lower or "radius" in q_lower or "circle" in q_lower or "triangle" in q_lower or "distance between" in q_lower or "angle" in q_lower or "geometry" in q_lower:
        return "Geometry"
    else:
        return "Arithmetic"


def validate_mcq(df: pd.DataFrame) -> bool:
    """Check required columns and value ranges."""
    if not all(col in df.columns for col in REQUIRED_MCQ_COLS):
        return False
    if not df["correct_option"].isin(["A", "B", "C", "D"]).all():
        return False
    if not df["difficulty_expert"].isin(["easy", "medium", "hard"]).all():
        return False
    return True


def load_mcq_bank(path=None) -> pd.DataFrame:
    """Load real MCQ CSV or fall back to mock data."""
    if path is not None:
        path = Path(path)
        try:
            if path.exists():
                try:
                    df = pd.read_csv(path, sep=";", encoding="latin1")
                except Exception:
                    try:
                        df = pd.read_csv(path, sep=None, engine="python")
                    except UnicodeDecodeError:
                        df = pd.read_csv(path, sep=None, engine="python", encoding="latin1")
                
                # Standardize column mapping
                mapping = {
                    "Question": "question",
                    "Choice_A": "option_a",
                    "Choice_B": "option_b",
                    "Choice_C": "option_c",
                    "Choice_D": "option_d",
                    "Correct_Answer": "correct_option",
                    "Difficulty": "difficulty_expert"
                }
                df = df.rename(columns={k: v for k, v in mapping.items() if k in df.columns})
                
                # Strip and normalize columns if they exist
                if "difficulty_expert" in df.columns:
                    df["difficulty_expert"] = df["difficulty_expert"].astype(str).str.lower().str.strip()
                if "correct_option" in df.columns:
                    df["correct_option"] = df["correct_option"].astype(str).str.upper().str.strip()
                
                if validate_mcq(df):
                    if "item_id" not in df.columns:
                        df["item_id"] = range(len(df))
                    df["domain"] = df["question"].apply(classify_domain)
                    return df
                    return df
                else:
                    warnings.warn(f"MCQ file {path} has invalid columns. Using mock data.")
        except Exception as e:
            warnings.warn(f"Error loading MCQ file: {e}. Using mock data.")
    
    df_mock = generate_mock_mcq()
    df_mock["domain"] = df_mock["question"].apply(classify_domain)
    return df_mock


def load_human_responses(path=None, mcq_df=None) -> pd.DataFrame:
    """Load real human responses CSV or fall back to mock data."""
    if path is not None:
        path = Path(path)
        try:
            if path.exists():
                try:
                    df = pd.read_csv(path, sep=None, engine="python")
                except UnicodeDecodeError:
                    df = pd.read_csv(path, sep=None, engine="python", encoding="latin1")
                if all(col in df.columns for col in REQUIRED_HUMAN_COLS):
                    return df
                else:
                    warnings.warn(f"Human responses file has invalid columns. Using mock data.")
        except Exception as e:
            warnings.warn(f"Error loading human responses: {e}. Using mock data.")
    if mcq_df is None:
        mcq_df = generate_mock_mcq()
    return generate_mock_human_responses(mcq_df)


def generate_mock_mcq(n=MOCK_N_ITEMS, seed=MOCK_RANDOM_SEED) -> pd.DataFrame:
    """Generate n realistic math MCQ items across four topics."""
    rng = np.random.RandomState(seed)
    items = []
    topics = ["algebra", "geometry", "equations", "arithmetic"]
    per_topic = n // len(topics)
    remainder = n - per_topic * len(topics)

    item_id = 0
    for t_idx, topic in enumerate(topics):
        count = per_topic + (1 if t_idx < remainder else 0)
        for _ in range(count):
            if topic == "algebra":
                a = rng.randint(2, 15)
                b = rng.randint(1, 20)
                c = rng.randint(5, 50)
                question = f"Solve: {a}x + {b} = {c}"
                correct_val = round((c - b) / a, 2)
            elif topic == "geometry":
                r = rng.randint(1, 25)
                question = f"Area of a circle with radius {r}"
                correct_val = round(3.14159 * r * r, 2)
            elif topic == "equations":
                a = rng.randint(1, 5)
                b = rng.randint(-10, 10)
                c = rng.randint(-15, 15)
                question = f"Find x: {a}x^2 + {b}x + {c} = 0"
                disc = b * b - 4 * a * c
                if disc >= 0:
                    correct_val = round((-b + disc**0.5) / (2 * a), 2)
                else:
                    correct_val = round(-b / (2 * a), 2)
            else:  # arithmetic
                a = rng.randint(2, 50)
                b = rng.randint(2, 50)
                c = rng.randint(1, 100)
                question = f"Calculate: {a} * {b} + {c}"
                correct_val = a * b + c

            # Generate distractors
            offsets = []
            while len(offsets) < 3:
                noise = rng.choice([-3, -2, -1, 1, 2, 3, 5, 10])
                dist = round(correct_val + noise * max(1, abs(correct_val) * 0.1), 2)
                if dist != correct_val and dist not in offsets:
                    offsets.append(dist)

            options = [correct_val] + offsets
            correct_pos = rng.randint(0, 4)
            options[0], options[correct_pos] = options[correct_pos], options[0]
            correct_letter = ["A", "B", "C", "D"][correct_pos]

            # Assign difficulty
            r_val = rng.random()
            if r_val < 0.40:
                difficulty = "easy"
            elif r_val < 0.75:
                difficulty = "medium"
            else:
                difficulty = "hard"

            items.append({
                "item_id": item_id,
                "question": question,
                "option_a": str(options[0]),
                "option_b": str(options[1]),
                "option_c": str(options[2]),
                "option_d": str(options[3]),
                "correct_option": correct_letter,
                "difficulty_expert": difficulty,
            })
            item_id += 1

    return pd.DataFrame(items)


def generate_mock_human_responses(
    mcq_df: pd.DataFrame,
    n_students=MOCK_N_HUMANS,
    seed=MOCK_RANDOM_SEED
) -> pd.DataFrame:
    """Simulate responses from n_students real students with varied abilities."""
    rng = np.random.RandomState(seed)

    n_low = int(n_students * 0.30)
    n_mid = int(n_students * 0.40)
    n_high = n_students - n_low - n_mid

    abilities = np.concatenate([
        rng.uniform(0.30, 0.50, size=n_low),
        rng.uniform(0.50, 0.70, size=n_mid),
        rng.uniform(0.70, 0.90, size=n_high)
    ])

    difficulty_multiplier = {"easy": 1.30, "medium": 1.00, "hard": 0.60}
    
    item_ids = mcq_df["item_id"].values
    n_items = len(item_ids)
    
    diffs = mcq_df.get("difficulty_expert", pd.Series(["medium"] * n_items)).values
    mults = np.array([difficulty_multiplier.get(d, 1.00) for d in diffs])

    p_matrix = abilities[:, np.newaxis] * mults[np.newaxis, :]
    p_matrix += rng.normal(0, 0.05, size=(n_students, n_items))
    p_matrix = np.clip(p_matrix, 0.01, 0.99)

    responses = (rng.random(size=(n_students, n_items)) < p_matrix).astype(int)
    student_ids = [f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)} (STU-{i:03d})" for i in range(n_students)]

    df_responses = pd.DataFrame(responses, index=student_ids, columns=item_ids)
    df_long = df_responses.reset_index().melt(
        id_vars="index", var_name="item_id", value_name="response"
    ).rename(columns={"index": "student_id"})
    
    return df_long
