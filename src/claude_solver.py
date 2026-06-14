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

    def _build_prompt(self, row: dict, infer_correct: bool = False, infer_difficulty: bool = False) -> str:
        correct_section = (
            f"Bonne réponse: {row.get('correct_option', 'A')}"
            if not infer_correct
            else "Bonne réponse: INCONNUE — tu dois la deviner depuis le contenu des options."
        )
        difficulty_section = (
            f"Difficulté déclarée: {row.get('difficulty_expert', 'medium')}"
            if not infer_difficulty
            else "Difficulté: INCONNUE — tu dois l'estimer depuis la complexité de la question."
        )
        return f"""Tu es le moteur de calibration psychométrique de PsychoCrowd.

Analyse ce QCM et retourne UNIQUEMENT un JSON valide :

Question: {row.get('question', '')}
A) {row.get('option_a', '')}
B) {row.get('option_b', '')}
C) {row.get('option_c', '')}
D) {row.get('option_d', '')}
{correct_section}
{difficulty_section}

Format JSON attendu (aucun texte avant ou après) :
{{
  "correct_option": "A",
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
- correct_option : la lettre (A/B/C/D) de la bonne réponse. Si elle t'est donnée, utilise-la. Sinon, déduis-la.
- confidence : ta certitude que la bonne réponse est évidente, entre 0.05 et 0.99
- difficulty_ai : easy / medium / hard (si donnée, respecte-la ; sinon, estime-la)
- error_types : type d'erreur cognitif pour chaque distracteur, null si c'est la bonne réponse
- distractor_weights : probabilité relative que chaque option incorrecte soit choisie. Doit sommer à 1.0 sur les incorrectes
- quality_score : 0-10 (qualité pédagogique)
- quality_flags : liste de problèmes (vide si aucun). Ajoute "correct_inferred" si tu as deviné la réponse, "difficulty_inferred" si tu as estimé la difficulté.
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

    def solve_item(self, row: dict, infer_correct: bool = False, infer_difficulty: bool = False) -> dict:
        prompt = self._build_prompt(row, infer_correct=infer_correct, infer_difficulty=infer_difficulty)
        result = self._call_with_retry(prompt)
        time.sleep(CLAUDE_DELAY_SEC)
        return result

    def solve_all(self, df: pd.DataFrame, progress_callback=None) -> pd.DataFrame:
        """
        Traiter tous les items.
        Détecte automatiquement si correct_option ou difficulty_expert sont absents
        et demande à Claude de les inférer depuis le texte des questions.
        Retourner df enrichi avec colonnes :
        correct_option (si inférée) | difficulty_expert (si inférée) |
        ai_confidence | ai_difficulty | error_types |
        distractor_weights | quality_score | quality_flags
        """
        df = df.copy()

        # Détection des colonnes manquantes
        infer_correct = (
            "correct_option" not in df.columns
            or not df["correct_option"].notna().any()
            or (df["correct_option"].astype(str).str.strip() == "").all()
        )
        infer_difficulty = (
            "difficulty_expert" not in df.columns
            or not df["difficulty_expert"].notna().any()
            or (df["difficulty_expert"].astype(str).str.strip() == "").all()
        )

        results = []
        total = len(df)
        for i, (_, row) in enumerate(df.iterrows()):
            result = self.solve_item(
                row.to_dict(),
                infer_correct=infer_correct,
                infer_difficulty=infer_difficulty
            )
            results.append(result)
            if progress_callback:
                progress_callback(i + 1, total)

        df["ai_confidence"]      = [r.get("confidence", 0.5)      for r in results]
        df["ai_difficulty"]      = [r.get("difficulty_ai","medium") for r in results]
        df["error_types"]        = [r.get("error_types",{})         for r in results]
        df["distractor_weights"] = [r.get("distractor_weights",{})  for r in results]
        df["quality_score"]      = [r.get("quality_score",5)        for r in results]
        df["quality_flags"]      = [r.get("quality_flags",[])       for r in results]

        # Écrire les valeurs inférées par Claude dans le dataframe
        if infer_correct:
            df["correct_option"] = [
                r.get("correct_option", "A") for r in results
            ]
        if infer_difficulty:
            df["difficulty_expert"] = [
                r.get("difficulty_ai", "medium") for r in results
            ]

        return df

