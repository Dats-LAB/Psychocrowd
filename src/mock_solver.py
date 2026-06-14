import numpy as np
import pandas as pd
from config import MOCK_RANDOM_SEED

class MockMCQSolver:
    """
    Solveur sans API. Génère des probabilités synthétiques
    cohérentes avec difficulty_expert.
    Activé automatiquement si ANTHROPIC_API_KEY absent.
    """

    def __init__(self, seed=MOCK_RANDOM_SEED):
        np.random.seed(seed)

    def solve_all(self, df: pd.DataFrame, progress_callback=None) -> pd.DataFrame:
        RANGES = {
            "easy":   (0.75, 0.95),
            "medium": (0.50, 0.75),
            "hard":   (0.25, 0.55),
        }
        results = []
        for i, (_, row) in enumerate(df.iterrows()):
            low, high = RANGES.get(
                str(row.get("difficulty_expert","medium")).lower(),
                (0.50, 0.75)
            )
            p = float(np.clip(
                np.random.uniform(low, high) + np.random.normal(0, 0.04),
                0.05, 0.99
            ))
            opts = ["A","B","C","D"]
            correct = str(row.get("correct_option","A")).upper()
            wrong = [o for o in opts if o != correct]
            weights = {correct: 0.0}
            base = np.random.dirichlet(np.ones(3))
            for j, w in enumerate(wrong):
                weights[w] = float(base[j])

            results.append({
                "ai_confidence":      p,
                "ai_difficulty":      row.get("difficulty_expert","medium"),
                "error_types":        {o: "mock_error" if o != correct else None for o in opts},
                "distractor_weights": weights,
                "quality_score":      round(np.random.uniform(6, 9), 1),
                "quality_flags":      [],
            })
            if progress_callback:
                progress_callback(i + 1, len(df))

        df = df.copy()
        for key in ["ai_confidence","ai_difficulty","error_types",
                    "distractor_weights","quality_score","quality_flags"]:
            df[key] = [r[key] for r in results]
        return df
