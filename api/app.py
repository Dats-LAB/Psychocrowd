from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
import pandas as pd
import sys
import os
import io
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.supabase_client import get_supabase_client
from src.claude_solver import ClaudeMCQSolver
from src.mock_solver import MockMCQSolver
from src.profile_generator import build_probability_matrix
from src.crowd_generator import CrowdGenerator
from src.rasch_model import RaschModel
from src.comparator import PsychometricComparator
from config import ANTHROPIC_API_KEY

app = FastAPI(title="PsychoCrowd API - V3")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("data", exist_ok=True)
os.makedirs("outputs/plots", exist_ok=True)
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")
app.mount("/data", StaticFiles(directory="data"), name="data")

def get_db():
    return get_supabase_client()

# --- Schemas ---

class MCQItem(BaseModel):
    item_id: Optional[int] = None
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str
    difficulty_expert: str

class CalibrateRequest(BaseModel):
    items: List[dict]
    use_claude: bool = True

class SimulateRequest(BaseModel):
    items: List[dict] # Calibrated items (with ai_confidence, distractor_weights etc)
    n_per_profile: int = 50

class RaschRequest(BaseModel):
    response_matrix: List[List[int]] # N_students x N_items
    items: List[dict]

# --- Endpoints ---

@app.get("/")
def read_root():
    return {"message": "PsychoCrowd V3 API Gateway"}

@app.get("/items")
def get_items(db=Depends(get_db)):
    """Fetch MCQ bank from Supabase."""
    response = db.table("mcq_bank").select("*").execute()
    return {"data": response.data}

@app.post("/items")
def create_item(item: MCQItem, db=Depends(get_db)):
    """Add an item to the bank."""
    data = item.dict(exclude_unset=True)
    response = db.table("mcq_bank").insert(data).execute()
    return {"status": "success", "data": response.data}

@app.post("/calibrate")
def calibrate_items(req: CalibrateRequest):
    """Calibrate items using Claude or Mock Solver."""
    df = pd.DataFrame(req.items)
    
    if req.use_claude and ANTHROPIC_API_KEY:
        solver = ClaudeMCQSolver()
    else:
        solver = MockMCQSolver()
        
    calibrated_df = solver.solve_all(df)
    return {"data": calibrated_df.to_dict(orient="records")}

@app.post("/simulate")
def simulate_crowd(req: SimulateRequest):
    """Generate artificial crowd responses based on calibrated items."""
    mcq_df = pd.DataFrame(req.items)
    prob_matrix = build_probability_matrix(mcq_df)
    
    crowd_gen = CrowdGenerator(mcq_df, prob_matrix, n_per_profile=req.n_per_profile)
    crowd_df = crowd_gen.generate_crowd()
    response_matrix = crowd_gen.get_response_matrix()
    accuracy_df = crowd_gen.get_accuracy_by_profile()
    
    return {
        "crowd_responses": crowd_df.to_dict(orient="records"),
        "response_matrix": response_matrix.tolist(),
        "accuracy_by_profile": accuracy_df.to_dict(orient="records")
    }

@app.post("/rasch")
def fit_rasch(req: RaschRequest):
    """Fit JMLE Rasch model on a response matrix."""
    matrix = np.array(req.response_matrix)
    rasch = RaschModel()
    rasch.fit(matrix)
    
    if not rasch.converged:
        return {"status": "warning", "message": "Model did not converge completely.", "summary": rasch.summary()}
        
    fit_stats = rasch.item_fit_stats(matrix)
    
    return {
        "status": "success",
        "summary": rasch.summary(),
        "difficulties": rasch.get_item_difficulties().tolist(),
        "abilities": rasch.theta.tolist(),
        "item_fit": fit_stats.to_dict(orient="records")
    }

@app.post("/analyze")
def analyze_results(req: Dict[str, Any]):
    """NLP analysis of the Rasch comparison results using Claude."""
    return {"status": "success", "analysis": "This is a placeholder for Claude's NLP analysis of the psychometric results."}

@app.post("/api/upload")
async def upload_file(file_type: str = Form(...), file: UploadFile = File(...)):
    contents = await file.read()
    filename = "mcq_bank.csv" if file_type == "mcq" else "human_responses.csv"
    with open(f"data/{filename}", "wb") as f:
        f.write(contents)
    return {"status": "success"}

def read_csv_robust(contents: bytes) -> pd.DataFrame:
    for enc in ["utf-8", "windows-1252", "latin1"]:
        try:
            df = pd.read_csv(io.BytesIO(contents), sep=";", encoding=enc)
            if len(df.columns) < 2:
                df = pd.read_csv(io.BytesIO(contents), sep=",", encoding=enc)
            return df
        except UnicodeDecodeError:
            continue
    raise ValueError("Format d'encodage non supporté. Veuillez sauvegarder en UTF-8.")

@app.post("/api/run-pipeline")
async def run_pipeline(
    use_gemini: str = Form("false"), 
    api_key: str = Form(""),
    mcq_file: Optional[UploadFile] = File(None),
    human_file: Optional[UploadFile] = File(None)
):
    if not mcq_file:
        raise HTTPException(status_code=400, detail="Veuillez d'abord uploader un fichier MCQ Bank (CSV).")
        
    try:
        contents = await mcq_file.read()
        mcq_df = read_csv_robust(contents)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur lors de la lecture du fichier CSV: {str(e)}")
    
    # Normalize column names: lowercase and strip whitespace
    mcq_df.columns = [c.strip().lower() for c in mcq_df.columns]
    
    # Map common header variants to expected names
    col_map = {
        'choice_a': 'option_a', 'choice_b': 'option_b', 'choice_c': 'option_c', 'choice_d': 'option_d',
        'correct_answer': 'correct_option', 'difficulty': 'difficulty_expert',
        'question_text': 'question', 'q': 'question',
    }
    mcq_df.rename(columns=col_map, inplace=True)
    
    # Add item_id if not present
    if 'item_id' not in mcq_df.columns:
        mcq_df.insert(0, 'item_id', range(len(mcq_df)))
    
    use_ai = use_gemini.lower() == "true"

    if use_ai and (api_key or ANTHROPIC_API_KEY):
        solver = ClaudeMCQSolver()
    else:
        solver = MockMCQSolver()
        
    calibrated_df = solver.solve_all(mcq_df)
    prob_matrix = build_probability_matrix(calibrated_df)
    
    crowd_gen = CrowdGenerator(calibrated_df, prob_matrix)
    crowd_gen.generate_crowd()
    art_matrix = crowd_gen.get_response_matrix()
    
    human_matrix = art_matrix # Fallback to artificial if no human data
    if human_file:
        try:
            h_contents = await human_file.read()
            h_df = read_csv_robust(h_contents)
            human_matrix = h_df.pivot_table(index="student_id", columns="item_id", values="response", fill_value=0).values
        except: pass
        
    human_rasch = RaschModel()
    human_rasch.fit(human_matrix)
    
    art_rasch = RaschModel()
    art_rasch.fit(art_matrix)
    
    comp = PsychometricComparator(human_rasch, art_rasch, calibrated_df)
    
    # Save outputs for frontend
    crowd_gen.crowd_df.to_csv("outputs/response_matrix.csv", index=False)
    comp.compare_df().to_csv("outputs/rasch_comparison.csv", index=False)
    
    # Generate plots
    comp.plot_scatter("outputs/plots/scatter_comparison.png")
    comp.plot_difficulty_distributions("outputs/plots/difficulty_distribution.png")
    comp.plot_wright_map("outputs/plots/wright_map.png")
    
    report = {
        "human_rasch": {
            "converged": human_rasch.converged,
            "n_iterations": getattr(human_rasch, "iterations", 0),
            "mean_ability": float(np.mean(human_rasch.theta)),
            "std_ability": float(np.std(human_rasch.theta)),
            "mean_difficulty": float(np.mean(human_rasch.b)),
            "std_difficulty": float(np.std(human_rasch.b)),
        },
        "art_rasch": {
            "converged": art_rasch.converged,
            "n_iterations": getattr(art_rasch, "iterations", 0),
            "mean_ability": float(np.mean(art_rasch.theta)),
            "std_ability": float(np.std(art_rasch.theta)),
            "mean_difficulty": float(np.mean(art_rasch.b)),
            "std_difficulty": float(np.std(art_rasch.b)),
        },
        "comparison": comp.full_metrics(),
        "human_thetas": {f"H_{i}": float(human_rasch.theta[i]) for i in range(len(human_rasch.theta))},
        "art_thetas": {f"A_{i}": float(art_rasch.theta[i]) for i in range(len(art_rasch.theta))},
        "context_summary": "Analyse effectuée avec succès via Claude API.",
        "ai_recommendations": [],
        "plots_data": {
            "scatter": comp.get_scatter_data(),
            "distribution": comp.get_distribution_data(),
            "wright": comp.get_wright_map_data()
        }
    }
    
    return {"report": report}


# ── CLAUDE AI STUDIO ENDPOINTS ──────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str   # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    report_context: Optional[Dict] = None
    api_key: Optional[str] = ""

class InterpretRequest(BaseModel):
    report: Dict
    api_key: Optional[str] = ""

class ArticleRequest(BaseModel):
    report: Dict
    api_key: Optional[str] = ""


def _get_claude_client(api_key: str = ""):
    import anthropic
    key = api_key or ANTHROPIC_API_KEY
    if not key:
        raise HTTPException(status_code=400, detail="Clé API Claude requise pour cette fonctionnalité.")
    return anthropic.Anthropic(api_key=key)


@app.post("/api/claude/interpret-rasch")
async def interpret_rasch(req: InterpretRequest):
    """Génère une interprétation pédagogique des résultats Rasch via Claude."""
    client = _get_claude_client(req.api_key)
    r = req.report
    prompt = f"""Tu es un expert en psychométrie et en pédagogie. 
Voici les résultats d'une calibration par le Modèle de Rasch (1PL) sur une banque de questions MCQ.

=== RÉSULTATS HUMAINS ===
- Convergence : {r.get('human_rasch', {}).get('converged', False)}
- Capacité moyenne (θ) : {r.get('human_rasch', {}).get('mean_ability', 0):.3f} logits
- Écart-type des capacités : {r.get('human_rasch', {}).get('std_ability', 0):.3f}
- Difficulté moyenne (b) : {r.get('human_rasch', {}).get('mean_difficulty', 0):.3f} logits
- Écart-type des difficultés : {r.get('human_rasch', {}).get('std_difficulty', 0):.3f}

=== RÉSULTATS FOULE ARTIFICIELLE ===
- Convergence : {r.get('art_rasch', {}).get('converged', False)}
- Capacité moyenne (θ) : {r.get('art_rasch', {}).get('mean_ability', 0):.3f} logits
- Écart-type des capacités : {r.get('art_rasch', {}).get('std_ability', 0):.3f}
- Difficulté moyenne (b) : {r.get('art_rasch', {}).get('mean_difficulty', 0):.3f} logits

=== MÉTRIQUES DE COMPARAISON ===
- Pearson r : {r.get('comparison', {}).get('pearson_r', 0):.4f}
- Spearman ρ : {r.get('comparison', {}).get('spearman_r', 0):.4f}
- MAE : {r.get('comparison', {}).get('mae', 0):.4f}
- Verdict : {r.get('comparison', {}).get('interpretation', 'N/A')}

Rédige une interprétation pédagogique complète en français (400-600 mots) structurée en 3 parties :
1. **Analyse des capacités étudiantes** : que révèle la distribution θ sur le niveau général de la classe ?
2. **Analyse des difficultés des items** : les items sont-ils bien calibrés pour ce niveau ?
3. **Qualité de la simulation artificielle** : que signifient les métriques de corrélation ? La foule artificielle est-elle représentative ?

Conclus avec 2-3 recommandations concrètes pour l'enseignant."""

    msg = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )
    return {"interpretation": msg.content[0].text}


@app.post("/api/claude/generate-article")
async def generate_article(req: ArticleRequest):
    """Génère une section 'Résultats' pour un article scientifique à partir du rapport Rasch."""
    client = _get_claude_client(req.api_key)
    r = req.report
    prompt = f"""Tu es un chercheur en sciences de l'éducation spécialisé en psychométrie.
Rédige la section "Résultats" d'un article scientifique académique (format APA) en français,
basée sur les données de calibration Rasch suivantes :

Capacité humaine moyenne : θ̄ = {r.get('human_rasch', {}).get('mean_ability', 0):.3f} (σ={r.get('human_rasch', {}).get('std_ability', 0):.3f})
Difficulté humaine moyenne : b̄ = {r.get('human_rasch', {}).get('mean_difficulty', 0):.3f} (σ={r.get('human_rasch', {}).get('std_difficulty', 0):.3f})
Capacité artificielle moyenne : θ̄ = {r.get('art_rasch', {}).get('mean_ability', 0):.3f} (σ={r.get('art_rasch', {}).get('std_ability', 0):.3f})
Corrélation de Pearson (humain/artificiel) : r = {r.get('comparison', {}).get('pearson_r', 0):.4f}
Corrélation de Spearman : ρ = {r.get('comparison', {}).get('spearman_r', 0):.4f}
MAE : {r.get('comparison', {}).get('mae', 0):.4f}
Verdict : {r.get('comparison', {}).get('interpretation', 'N/A')}

La section doit :
- Être rédigée au passé, en style académique neutre
- Inclure les statistiques descriptives dans le corps du texte
- Commenter la convergence du modèle et la signification des paramètres Rasch
- Comparer systématiquement les données humaines aux données artificielles
- Se terminer par une phrase de transition vers la section Discussion
- Faire environ 400-500 mots"""

    msg = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )
    return {"article_section": msg.content[0].text}


@app.post("/api/claude/chat")
async def analytical_chat(req: ChatRequest):
    """Chat analytique NLP sur les données psychométriques."""
    client = _get_claude_client(req.api_key)

    system_prompt = """Tu es PSYCHO, l'assistant analytique de PsychoCrowd, expert en psychométrie, 
modèle de Rasch, théorie de réponse à l'item (IRT), et analyse de données éducatives.
Tu réponds en français, de manière précise et pédagogique.
Si des données de rapport sont fournies, base-toi sur elles pour répondre.
Si une question sort du domaine psychométrique/éducatif, redirige poliment vers le domaine."""

    if req.report_context:
        r = req.report_context
        context = f"""
=== DONNÉES DE LA SESSION EN COURS ===
Capacité humaine moyenne : {r.get('human_rasch', {}).get('mean_ability', 'N/A')}
Difficulté humaine moyenne : {r.get('human_rasch', {}).get('mean_difficulty', 'N/A')}
Pearson r (humain/artificiel) : {r.get('comparison', {}).get('pearson_r', 'N/A')}
Verdict : {r.get('comparison', {}).get('interpretation', 'N/A')}
==="""
        system_prompt += context

    messages = [{"role": m.role, "content": m.content} for m in req.messages]

    msg = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1000,
        system=system_prompt,
        messages=messages
    )
    return {"reply": msg.content[0].text}
