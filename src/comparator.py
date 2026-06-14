import numpy as np
import pandas as pd
from scipy import stats
from config import PROFILE_TARGETS, PROFILES

class PsychometricComparator:
    """Compares human Rasch results to artificial crowd Rasch results and returns JSON-serializable data."""

    def __init__(self, human_rasch, artificial_rasch, mcq_df):
        self.human_rasch = human_rasch
        self.art_rasch = artificial_rasch
        self.mcq_df = mcq_df
        n_items = min(len(human_rasch.b), len(artificial_rasch.b))
        self.b_human = human_rasch.b[:n_items]
        self.b_art = artificial_rasch.b[:n_items]

    def pearson_r(self) -> float:
        r, _ = stats.pearsonr(self.b_human, self.b_art)
        return float(r)

    def spearman_r(self) -> float:
        r, _ = stats.spearmanr(self.b_human, self.b_art)
        return float(r)

    def mae(self) -> float:
        return float(np.mean(np.abs(self.b_human - self.b_art)))

    def rmse(self) -> float:
        return float(np.sqrt(np.mean((self.b_human - self.b_art) ** 2)))

    def compare_df(self) -> pd.DataFrame:
        n = len(self.b_human)
        delta = self.b_art - self.b_human
        abs_delta = np.abs(delta)
        agreement = []
        for d in abs_delta:
            if d < 0.50:
                agreement.append("strong")
            elif d < 1.00:
                agreement.append("moderate")
            else:
                agreement.append("weak")
        return pd.DataFrame({
            "item_id": range(n),
            "b_human": self.b_human,
            "b_artificial": self.b_art,
            "delta": delta,
            "abs_delta": abs_delta,
            "agreement": agreement,
        })

    def interpretation(self) -> str:
        r = self.pearson_r()
        if r >= 0.90: return "Excellent"
        if r >= 0.75: return "Bon"
        if r >= 0.60: return "Passable"
        return "Insuffisant"

    def full_metrics(self) -> dict:
        return {
            "pearson_r":      self.pearson_r(),
            "spearman_r":     self.spearman_r(),
            "mae":            self.mae(),
            "rmse":           self.rmse(),
            "interpretation": self.interpretation(),
        }

    def get_scatter_data(self) -> list:
        """Returns data for a scatter plot of b_human vs b_artificial."""
        comp = self.compare_df()
        return comp.to_dict(orient="records")

    def get_distribution_data(self) -> dict:
        """Returns histograms for difficulty distributions."""
        h_hist, h_bins = np.histogram(self.b_human, bins=30, density=True)
        a_hist, a_bins = np.histogram(self.b_art, bins=30, density=True)
        return {
            "human": {
                "counts": h_hist.tolist(),
                "bins": h_bins.tolist()
            },
            "artificial": {
                "counts": a_hist.tolist(),
                "bins": a_bins.tolist()
            }
        }

    def get_wright_map_data(self) -> dict:
        """Returns data to construct a Wright map on the frontend."""
        # Histograms for theta (abilities) and b (difficulties)
        t_h_hist, t_h_bins = np.histogram(self.human_rasch.theta, bins=25)
        t_a_hist, t_a_bins = np.histogram(self.art_rasch.theta, bins=25)
        b_h_hist, b_h_bins = np.histogram(self.b_human, bins=25)
        b_a_hist, b_a_bins = np.histogram(self.b_art, bins=25)

        return {
            "abilities": {
                "human": {"counts": t_h_hist.tolist(), "bins": t_h_bins.tolist()},
                "artificial": {"counts": t_a_hist.tolist(), "bins": t_a_bins.tolist()}
            },
            "difficulties": {
                "human": {"counts": b_h_hist.tolist(), "bins": b_h_bins.tolist()},
                "artificial": {"counts": b_a_hist.tolist(), "bins": b_a_bins.tolist()}
            }
        }

    def get_profile_perf_data(self, crowd_df: pd.DataFrame) -> dict:
        """Returns accuracy data grouped by profile and difficulty."""
        perf = (
            crowd_df
            .groupby(["difficulty", "profile"])["is_correct"]
            .mean()
            .reset_index()
            .rename(columns={"is_correct": "accuracy"})
        )
        
        difficulties = ["easy", "medium", "hard"]
        profiles_list = list(PROFILES.keys())
        
        data = []
        for diff in difficulties:
            row = {"difficulty": diff}
            for profile in profiles_list:
                mask = (perf["difficulty"] == diff) & (perf["profile"] == profile)
                subset = perf[mask]
                val = subset["accuracy"].values[0] if len(subset) > 0 else 0
                row[profile] = float(val)
                row[f"{profile}_target"] = float(PROFILE_TARGETS.get(profile, [0,0,0])[difficulties.index(diff)])
            data.append(row)
            
        return data
