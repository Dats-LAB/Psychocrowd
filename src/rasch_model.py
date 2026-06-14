import numpy as np
import pandas as pd
from config import RASCH_MAX_ITER, RASCH_TOL

class RaschModel:
    """
    Modèle de Rasch 1-PL — JMLE from scratch (numpy + scipy uniquement).
    """

    def __init__(self, max_iter=RASCH_MAX_ITER, tol=RASCH_TOL):
        self.max_iter = max_iter
        self.tol = tol
        self.theta = None   # (n_students,)
        self.b     = None   # (n_items,)
        self.converged = False
        self.n_iter    = 0

    @staticmethod
    def _logistic(x):
        return 1 / (1 + np.exp(-np.clip(x, -30, 30)))

    def fit(self, R: np.ndarray):
        """
        R : matrice binaire (n_students × n_items).
        Algorithme JMLE :
        1. Init : theta = logit(r_i / J), b = -logit(s_j / N)
           avec correction 0.3 pour scores extrêmes.
        2. Alternance mises à jour Newton-Raphson :
           theta_i += (r_i - sum_j P_ij) / sum_j P_ij(1-P_ij)
           b_j     += (sum_i P_ij - s_j) / sum_i P_ij(1-P_ij)
        3. Centrage b à chaque itération.
        4. Convergence : max(|delta|) < tol
        """
        N, J = R.shape
        r_i = np.sum(R, axis=1) # scores des étudiants
        s_j = np.sum(R, axis=0) # scores des items

        # Correction des scores extrêmes (0 ou max)
        r_i_adj = np.clip(r_i, 0.3, J - 0.3)
        s_j_adj = np.clip(s_j, 0.3, N - 0.3)

        # Initialisation via logit
        self.theta = np.log(r_i_adj / (J - r_i_adj))
        self.b = -np.log(s_j_adj / (N - s_j_adj))

        for iter_num in range(self.max_iter):
            # Calcul probabilités P_ij
            diff = self.theta[:, np.newaxis] - self.b[np.newaxis, :]
            P = self._logistic(diff)
            W = P * (1 - P) # Variance P(1-P)

            # Mise à jour theta
            delta_theta = (r_i - np.sum(P, axis=1)) / np.sum(W, axis=1)
            self.theta += delta_theta

            # Mise à jour b
            # diff = self.theta[:, np.newaxis] - self.b[np.newaxis, :]
            # P = self._logistic(diff)
            # W = P * (1 - P)
            delta_b = (np.sum(P, axis=0) - s_j) / np.sum(W, axis=0)
            self.b += delta_b

            # Centrage de b
            mean_b = np.mean(self.b)
            self.b -= mean_b
            self.theta -= mean_b

            # Vérification de la convergence
            max_delta = max(np.max(np.abs(delta_theta)), np.max(np.abs(delta_b)))
            if max_delta < self.tol:
                self.converged = True
                self.n_iter = iter_num + 1
                break
        
        if not self.converged:
            self.n_iter = self.max_iter

    def item_fit_stats(self, R: np.ndarray) -> pd.DataFrame:
        """
        Infit MNSQ par item.
        Flag : <0.7 overfit | >1.3 underfit | sinon acceptable
        """
        if self.theta is None or self.b is None:
            raise ValueError("Modèle non fitté.")
            
        N, J = R.shape
        diff = self.theta[:, np.newaxis] - self.b[np.newaxis, :]
        P = self._logistic(diff)
        W = P * (1 - P) # Variance P_ij(1-P_ij)
        
        # Résidus standardisés
        Z = (R - P) / np.sqrt(W + 1e-10)
        
        # Infit mean-square = sum_i (W_ij * Z_ij^2) / sum_i W_ij
        # Puisque Z^2 = (R-P)^2 / W, alors W * Z^2 = (R-P)^2
        infit_mnsq = np.sum((R - P)**2, axis=0) / np.sum(W, axis=0)
        
        df = pd.DataFrame({
            'item_idx': range(J),
            'b': self.b,
            'infit_mnsq': infit_mnsq
        })
        
        df['fit_status'] = 'acceptable'
        df.loc[df['infit_mnsq'] < 0.7, 'fit_status'] = 'overfit'
        df.loc[df['infit_mnsq'] > 1.3, 'fit_status'] = 'underfit'
        
        return df

    def get_item_difficulties(self) -> np.ndarray:
        return self.b

    def summary(self) -> dict:
        if self.theta is None or self.b is None:
            return {"converged": False, "error": "Model not fitted"}
            
        return {
            "converged":    bool(self.converged),
            "n_iter":       int(self.n_iter),
            "mean_b":       float(np.mean(self.b)),
            "std_b":        float(np.std(self.b)),
            "mean_theta":   float(np.mean(self.theta)),
            "std_theta":    float(np.std(self.theta)),
            "b_range":      [float(np.min(self.b)), float(np.max(self.b))],
        }
