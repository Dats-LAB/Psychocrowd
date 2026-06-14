import anthropic
import json
import time
import pandas as pd
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, CLAUDE_MAX_TOKENS, CLAUDE_DELAY_SEC, CLAUDE_MAX_RETRY, CLAUDE_RETRY_WAIT

class ClaudeMCQSolver:
    """
    Unique solveur IA de PsychoCrowd.
    Utilise Claude API pour estimer P(correct) par item
    et classifier les types d'erreurs cognitives par distracteur.
    NE GÉNÈRE PAS de nouveaux items.
    """

    def __init__(self, api_key=ANTHROPIC_API_KEY, model=CLAUDE_MODEL):
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY manquante. "
                "Ajoutez-la dans .env ou utilisez MockSolver."
            )
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def _build_prompt(self, row: dict) -> str:
        return f"""Tu es le moteur de calibration psychométrique de PsychoCrowd.

Analyse ce QCM de mathématiques et retourne UNIQUEMENT un JSON valide :

Question: {row.get('question', '')}
A) {row.get('option_a', '')}
B) {row.get('option_b', '')}
C) {row.get('option_c', '')}
D) {row.get('option_d', '')}
Bonne réponse: {row.get('correct_option', 'A')}

Format JSON attendu (aucun texte avant ou après) :
{{
  "confidence": 0.75,
  "difficulty_ai": "medium",
  "error_types": {{
    "A": null,
    "B": null,
    "C": null,
    "D": null
  }},
  "distractor_weights": {{
    "A": 0.33,
    "B": 0.33,
    "C": 0.33,
    "D": 0.33
  }},
  "quality_score": 8,
  "quality_flags": []
}}

Règles strictes :
- confidence : ta certitude que la bonne réponse est évidente,
  entre 0.05 et 0.99 (0.95 = très facile, 0.40 = difficile)
- difficulty_ai : easy / medium / hard
- error_types : type d'erreur cognitif pour chaque distracteur,
  null si c'est la bonne réponse.
  Types possibles : confusion_signe | calcul_approximatif |
  formule_incorrecte | hors_domaine | confusion_variable
- distractor_weights : probabilité relative que chaque option
  incorrecte soit choisie en cas d'erreur. Doit sommer à 1.0
  sur les options incorrectes.
- quality_score : 0-10 (qualité pédagogique de l'item)
- quality_flags : liste de problèmes détectés (vide si aucun)
"""

    def _call_with_retry(self, prompt: str) -> dict:
        for attempt in range(CLAUDE_MAX_RETRY):
            try:
                msg = self.client.messages.create(
                    model=self.model,
                    max_tokens=CLAUDE_MAX_TOKENS,
                    messages=[{"role":"user","content":prompt}]
                )
                raw = msg.content[0].text.strip()
                raw = raw.replace("```json","").replace("```","").strip()
                data = json.loads(raw)
                # Validation minimale
                assert "confidence" in data
                data["confidence"] = float(
                    max(0.05, min(0.99, data.get("confidence", 0.5)))
                )
                return data
            except Exception as e:
                if attempt < CLAUDE_MAX_RETRY - 1:
                    time.sleep(CLAUDE_RETRY_WAIT)
                else:
                    return {
                        "confidence": 0.50,
                        "difficulty_ai": "medium",
                        "error_types": {},
                        "distractor_weights": {"A":0.33,"B":0.33,"C":0.33,"D":0.33},
                        "quality_score": 5,
                        "quality_flags": ["api_error"]
                    }

    def solve_item(self, row: dict) -> dict:
        prompt = self._build_prompt(row)
        result = self._call_with_retry(prompt)
        time.sleep(CLAUDE_DELAY_SEC)
        return result

    def solve_all(self, df: pd.DataFrame, progress_callback=None) -> pd.DataFrame:
        """
        Traiter tous les items.
        Retourner df enrichi avec colonnes :
        ai_confidence | ai_difficulty | error_types |
        distractor_weights | quality_score | quality_flags
        """
        results = []
        total = len(df)
        for i, (_, row) in enumerate(df.iterrows()):
            result = self.solve_item(row.to_dict())
            results.append(result)
            if progress_callback:
                progress_callback(i + 1, total)

        df = df.copy()
        df["ai_confidence"]      = [r.get("confidence", 0.5) for r in results]
        df["ai_difficulty"]      = [r.get("difficulty_ai","medium") for r in results]
        df["error_types"]        = [r.get("error_types",{}) for r in results]
        df["distractor_weights"] = [r.get("distractor_weights",{}) for r in results]
        df["quality_score"]      = [r.get("quality_score",5) for r in results]
        df["quality_flags"]      = [r.get("quality_flags",[]) for r in results]
        return df
