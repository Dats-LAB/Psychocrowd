import numpy as np
import pandas as pd
from config import PROFILES, N_STUDENTS_PER_PROFILE, MOCK_RANDOM_SEED

class CrowdGenerator:
    """Generates artificial student crowds with profile-based response patterns."""

    def __init__(self, mcq_df, probability_matrix,
                 n_per_profile=N_STUDENTS_PER_PROFILE,
                 seed=MOCK_RANDOM_SEED):
        self.mcq_df = mcq_df.copy()
        # Ensure item_id column exists
        if 'item_id' not in self.mcq_df.columns:
            self.mcq_df.insert(0, 'item_id', range(len(self.mcq_df)))
        self.prob_matrix = probability_matrix
        self.n_per_profile = n_per_profile
        self.rng = np.random.RandomState(seed)
        self.crowd_df = None


    def _generate_response(self, p_correct: float, correct_opt: str,
                            distractor_weights: dict) -> tuple:
        """
        Tirage de Bernoulli.
        Si correct -> (correct_opt, 1)
        Si incorrect -> distracteur pondéré selon distractor_weights -> (chosen_opt, 0)
        """
        if self.rng.random() < p_correct:
            return (correct_opt, 1)
        else:
            # S'il n'y a pas de poids, on fait un tirage uniforme parmi les autres options
            opts = ["A", "B", "C", "D"]
            wrong_opts = [o for o in opts if o != correct_opt]
            
            if distractor_weights and sum(distractor_weights.get(o, 0) for o in wrong_opts) > 0:
                weights = [distractor_weights.get(o, 0) for o in wrong_opts]
                # Normalisation
                total = sum(weights)
                probs = [w / total for w in weights]
                chosen = self.rng.choice(wrong_opts, p=probs)
            else:
                chosen = self.rng.choice(wrong_opts)
                
            return (chosen, 0)

    def generate_crowd(self) -> pd.DataFrame:
        """
        Étudiants artificiels (N_STUDENTS_PER_PROFILE × 4 profils).
        student_id format : ART_{profile}_{n:03d}
        Colonnes : student_id | profile | item_id | chosen_option | is_correct
        """
        profiles = list(PROFILES.keys())
        all_records = []

        prob_dict = {}
        for profile in profiles:
            mapping = self.prob_matrix.set_index("item_id")[f"p_{profile}"].to_dict()
            prob_dict[profile] = mapping

        for profile in profiles:
            p_map = prob_dict[profile]
            student_ids = [f"ART_{profile}_{s_num:03d}" for s_num in range(1, self.n_per_profile + 1)]
            
            for _, mcq_row in self.mcq_df.iterrows():
                item_id = mcq_row["item_id"]
                p_correct = p_map.get(item_id, 0.5)
                correct_option = mcq_row["correct_option"]
                diff = mcq_row.get("difficulty_expert", "medium")
                distractor_weights = mcq_row.get("distractor_weights", {})
                
                for s_id in student_ids:
                    chosen, is_correct = self._generate_response(p_correct, correct_option, distractor_weights)
                    
                    all_records.append({
                        "student_id": s_id,
                        "profile": profile,
                        "item_id": item_id,
                        "difficulty": diff,
                        "chosen_option": chosen,
                        "is_correct": is_correct,
                    })

        self.crowd_df = pd.DataFrame(all_records)
        return self.crowd_df

    def get_response_matrix(self) -> np.ndarray:
        """Pivot crowd_df to binary matrix (n_students x n_items)."""
        if self.crowd_df is None:
            self.generate_crowd()
        pivot = self.crowd_df.pivot_table(
            index="student_id", columns="item_id",
            values="is_correct", fill_value=0
        )
        return pivot.values

    def get_accuracy_by_profile(self) -> pd.DataFrame:
        """Return mean accuracy per profile per difficulty level."""
        if self.crowd_df is None:
            self.generate_crowd()
        return (
            self.crowd_df
            .groupby(["profile", "difficulty"])["is_correct"]
            .mean()
            .reset_index()
            .rename(columns={"is_correct": "accuracy"})
        )
