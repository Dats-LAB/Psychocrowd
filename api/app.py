from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import pandas as pd
import sys
import os
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
    # To be implemented when frontend sends comparison data
    return {"status": "success", "analysis": "This is a placeholder for Claude's NLP analysis of the psychometric results."}
