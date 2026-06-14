# config.py
"""Central configuration for the PsychoCrowd project."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Paths ──────────────────────────────────────────────────────────────
BASE_DIR          = Path(__file__).parent
DATA_DIR          = BASE_DIR / "data"
OUTPUTS_DIR       = BASE_DIR / "outputs"
PLOTS_DIR         = OUTPUTS_DIR / "plots"
MCQ_PATH          = DATA_DIR / "mcq_bank.csv"
HUMAN_PATH        = DATA_DIR / "human_responses.csv"

# ── Claude API ──────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL      = "claude-3-5-sonnet-20241022"
CLAUDE_MAX_TOKENS = 512
CLAUDE_DELAY_SEC  = 1.0
CLAUDE_MAX_RETRY  = 3
CLAUDE_RETRY_WAIT = 10

# ── Supabase ────────────────────────────────────────────────────────────
SUPABASE_URL      = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY      = os.getenv("SUPABASE_KEY", "")

# ── Mock data parameters ────────────────────────────────────────────────
MOCK_N_ITEMS      = 1000
MOCK_N_HUMANS     = 200
MOCK_RANDOM_SEED  = 42

# ── Student profiles ────────────────────────────────────────────────────
PROFILES = {
    "expert": +0.20,
    "good":   +0.05,
    "medium": -0.10,
    "weak":   -0.30,
}
N_STUDENTS_PER_PROFILE = 50    # 4 profiles × 50 = 200 artificial students

# ── Performance targets by difficulty ──────────────────────────────────
PROFILE_TARGETS = {
    #            easy   medium  hard
    "weak":    [0.45,   0.30,   0.15],
    "medium":  [0.70,   0.55,   0.35],
    "good":    [0.85,   0.75,   0.60],
    "expert":  [0.97,   0.93,   0.85],
}

# ── Rasch model ─────────────────────────────────────────────────────────
RASCH_MAX_ITER    = 200
RASCH_TOL         = 1e-6

# ── Visualization ───────────────────────────────────────────────────────
PLOT_STYLE        = "seaborn-v0_8-whitegrid"
PLOT_FIGSIZE      = (11, 7)
PLOT_DPI          = 150
BRAND_COLORS      = {
    "primary":    "#1B3A6B",   # navy
    "secondary":  "#00A8CC",   # cyan
    "accent":     "#7B2FBE",   # violet
    "human":      "#E63946",   # red
    "artificial": "#2EC4B6",   # teal
    "weak":       "#FF6B6B",
    "medium":     "#FFD166",
    "good":       "#06D6A0",
    "expert":     "#118AB2",
}
