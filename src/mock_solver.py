import numpy as np
import pandas as pd
from config import MOCK_RANDOM_SEED

class MockMCQSolver:
    """
    Solveur sans API. Génère des probabilités synthétiques
    cohérentes avec difficulty_expert.
    Si correct_option ou difficulty_expert sont absents du CSV,
    les infère automatiquement par heuristiques textuelles.
    Activé automatiquement si ANTHROPIC_API_KEY absent.
    """

    def __init__(self, seed=MOCK_RANDOM_SEED):
        np.random.seed(seed)

    @staticmethod
    def _infer_correct_option(row: pd.Series) -> str:
        """
        En l'absence de correct_option, choisit l'option la plus probable
        comme bonne réponse via heuristique : l'option la plus longue
        (généralement la plus précise pédagogiquement).
        """
        opts = {
            "A": str(row.get("option_a", "")),
            "B": str(row.get("option_b", "")),
            "C": str(row.get("option_c", "")),
            "D": str(row.get("option_d", "")),
        }
        return max(opts, key=lambda k: len(opts[k]))

    @staticmethod
    def _infer_difficulty(row: pd.Series) -> str:
        """
        Estime la difficulté depuis la longueur + symboles mathématiques.
          score < 80  → easy
          score < 160 → medium
          score >= 160 → hard
        """
        q = str(row.get("question", ""))
        math_symbols = sum(q.count(s) for s in ["int", "sum", "lim", "d/dx", "sqrt", "^2", "^3", "partial", "delta"])
        score = len(q) + math_symbols * 20
        if score < 80:
            return "easy"
        elif score < 160:
            return "medium"
        else:
            return "hard"

    def solve_all(self, df: pd.DataFrame, progress_callback=None) -> pd.DataFrame:
        df = df.copy()

        # ── Auto-complétion des colonnes manquantes ──────────────────────────
        has_correct = (
            "correct_option" in df.columns
            and df["correct_option"].notna().any()
            and (df["correct_option"].astype(str).str.strip() != "").any()
        )
        has_difficulty = (
            "difficulty_expert" in df.columns
            and df["difficulty_expert"].notna().any()
            and (df["difficulty_expert"].astype(str).str.strip() != "").any()
        )

        if not has_correct:
            df["correct_option"] = df.apply(self._infer_correct_option, axis=1)

        if not has_difficulty:
            df["difficulty_expert"] = df.apply(self._infer_difficulty, axis=1)

        RANGES = {
            "easy":   (0.75, 0.95),
            "medium": (0.50, 0.75),
            "hard":   (0.25, 0.55),
        }
        results = []
        for i, (_, row) in enumerate(df.iterrows()):
            low, high = RANGES.get(
                str(row.get("difficulty_expert", "medium")).lower().strip(),
                (0.50, 0.75)
            )
            p = float(np.clip(
                np.random.uniform(low, high) + np.random.normal(0, 0.04),
                0.05, 0.99
            ))
            opts = ["A", "B", "C", "D"]
            correct = str(row.get("correct_option", "A")).upper().strip()
            if correct not in opts:
                correct = "A"
            wrong = [o for o in opts if o != correct]
            weights = {correct: 0.0}
            base = np.random.dirichlet(np.ones(3))
            for j, w in enumerate(wrong):
                weights[w] = float(base[j])

            quality_flags = []
            if not has_correct:
                quality_flags.append("correct_inferred")
            if not has_difficulty:
                quality_flags.append("difficulty_inferred")

            results.append({
                "ai_confidence":      p,
                "ai_difficulty":      row.get("difficulty_expert", "medium"),
                "error_types":        {o: "mock_error" if o != correct else None for o in opts},
                "distractor_weights": weights,
                "quality_score":      round(np.random.uniform(6, 9), 1),
                "quality_flags":      quality_flags,
            })
            if progress_callback:
                progress_callback(i + 1, len(df))

        for key in ["ai_confidence", "ai_difficulty", "error_types",
                    "distractor_weights", "quality_score", "quality_flags"]:
            df[key] = [r[key] for r in results]
        return df
