import json
import time
import pandas as pd
from google import genai
from google.genai import types
from config import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_DELAY_SEC, GEMINI_MAX_RETRY, GEMINI_RETRY_WAIT

class GeminiMCQSolver:
    """
    Solveur IA de PsychoCrowd basé sur Gemini.
    Estime P(correct) par item et classifie les types d'erreurs cognitives.
    """

    def __init__(self, api_key=GEMINI_API_KEY, model=GEMINI_MODEL):
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY manquante. "
                "Ajoutez-la dans .env ou utilisez MockSolver."
            )
        self.client = genai.Client(api_key=api_key)
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
        for attempt in range(GEMINI_MAX_RETRY):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.0,
                        response_mime_type="application/json"
                    )
                )
                raw = response.text.strip()
                raw = raw.replace("```json","").replace("```","").strip()
                data = json.loads(raw)
                # Validation minimale
                assert "confidence" in data
                data["confidence"] = float(
                    max(0.05, min(0.99, data.get("confidence", 0.5)))
                )
                return data
            except Exception as e:
                if attempt < GEMINI_MAX_RETRY - 1:
                    time.sleep(GEMINI_RETRY_WAIT)
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
        time.sleep(GEMINI_DELAY_SEC)
        return result

    def solve_all(self, df: pd.DataFrame, progress_callback=None) -> pd.DataFrame:
        df = df.copy()

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

        if infer_correct:
            df["correct_option"] = [
                r.get("correct_option", "A") for r in results
            ]
        if infer_difficulty:
            df["difficulty_expert"] = [
                r.get("difficulty_ai", "medium") for r in results
            ]

        return df
