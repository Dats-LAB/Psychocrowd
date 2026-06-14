"""
PsychoCrowd — Main Pipeline
Run: python main.py
"""

import json
import time
from datetime import datetime
from pathlib import Path
from config import *
from src.data_loader import load_mcq_bank, load_human_responses
from src.normalizer import normalize_dataframe
from src.mock_solver import MockMCQSolver
from src.profile_generator import build_probability_matrix, print_profile_summary
from src.crowd_generator import CrowdGenerator
from src.rasch_model import RaschModel
from src.comparator import PsychometricComparator


def log(msg):
    """Print timestamped log message."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def run_pipeline(use_gemini=False, api_key=None):
    """
    Full end-to-end PsychoCrowd pipeline.

    use_gemini=False → uses MockMCQSolver (default, no API key needed)
    use_gemini=True  → uses GeminiMCQSolver (requires GEMINI_API_KEY in .env)
    """

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    # ── Step 1: Load data ───────────────────────────────────────────────
    log("Step 1/8 — Loading MCQ bank...")
    mcq_df = load_mcq_bank(MCQ_PATH)
    log(f"         {len(mcq_df)} items loaded "
        f"({'real' if MCQ_PATH.exists() else 'mock'} data)")

    log("Step 1/8 — Loading human responses...")
    human_df = load_human_responses(HUMAN_PATH, mcq_df)
    log(f"         {human_df['student_id'].nunique()} students, "
        f"{len(human_df)} responses "
        f"({'real' if HUMAN_PATH.exists() else 'mock'} data)")

    # ── Step 2: Normalize ────────────────────────────────────────────────
    log("Step 2/8 — Normalizing math symbols...")
    mcq_df = normalize_dataframe(mcq_df)

    # ── Step 3: Solve MCQs ───────────────────────────────────────────────
    log("Step 3/8 — Solving MCQs with AI...")
    if use_gemini:
        from src.gemini_solver import GeminiMCQSolver
        solver = GeminiMCQSolver(api_key=api_key or GEMINI_API_KEY)
        log("         Using Gemini API (real AI confidence scores)")
        context_summary = solver.assimilate_bank(mcq_df)
    else:
        solver = MockMCQSolver()
        log("         Using MockSolver (no API key required)")
        context_summary = "Mock data context."

    mcq_df = solver.solve_all(mcq_df)

    # ── Step 4: Build probability matrix ────────────────────────────────
    log("Step 4/8 — Building student profile probability matrix...")
    prob_matrix = build_probability_matrix(mcq_df)
    print_profile_summary(prob_matrix)

    # ── Step 5: Generate artificial crowd ───────────────────────────────
    log("Step 5/8 — Generating artificial student crowd...")
    crowd_gen = CrowdGenerator(mcq_df, prob_matrix)
    crowd_df = crowd_gen.generate_crowd()
    art_matrix = crowd_gen.get_response_matrix()
    crowd_df.to_csv(OUTPUTS_DIR / "response_matrix.csv", index=False)
    log(f"         {crowd_df['student_id'].nunique()} artificial students generated")

    # ── Step 6: Rasch on human data ─────────────────────────────────────
    log("Step 6/8 — Fitting Rasch model to human responses...")
    human_pivot = (
        human_df.pivot(index="student_id",
                       columns="item_id",
                       values="response")
        .fillna(0)
    )
    human_student_ids = human_pivot.index.tolist()
    human_matrix = human_pivot.values
    human_rasch = RaschModel()
    human_rasch.fit(human_matrix)
    log(f"         Converged: {human_rasch.converged} "
        f"in {human_rasch.n_iter} iterations")

    # ── Step 7: Rasch on artificial crowd ───────────────────────────────
    log("Step 7/8 — Fitting Rasch model to artificial crowd...")
    art_pivot = crowd_df.pivot_table(index="student_id", columns="item_id", values="is_correct", fill_value=0)
    art_student_ids = art_pivot.index.tolist()
    art_rasch = RaschModel()
    art_rasch.fit(art_matrix)
    log(f"         Converged: {art_rasch.converged} "
        f"in {art_rasch.n_iter} iterations")

    # ── Step 8: Compare & report ─────────────────────────────────────────
    log("Step 8/8 — Comparing human vs artificial psychometrics...")
    comparator = PsychometricComparator(human_rasch, art_rasch, mcq_df)

    comparison_df = comparator.compare_difficulties()
    comparison_df.to_csv(OUTPUTS_DIR / "rasch_comparison.csv", index=False)

    comparator.plot_scatter(
        PLOTS_DIR / "scatter_comparison.png")
    comparator.plot_difficulty_distributions(
        PLOTS_DIR / "difficulty_distribution.png")
    comparator.plot_wright_map(
        PLOTS_DIR / "wright_map.png")
    comparator.plot_profile_performance(
        crowd_df, PLOTS_DIR / "profile_performance.png")

    metrics = comparator.full_metrics()
    
    ai_recommendations = []
    if use_gemini:
        ai_recommendations = solver.analyze_student_errors(mcq_df, crowd_df)

    # Build student ability mappings
    human_thetas = {sid: float(t) for sid, t in zip(human_student_ids, human_rasch.theta)}
    art_thetas = {sid: float(t) for sid, t in zip(art_student_ids, art_rasch.theta)}

    report = {
        "run_timestamp":    datetime.now().isoformat(),
        "data_source":      "real" if MCQ_PATH.exists() else "mock",
        "solver":           "gemini" if use_gemini else "mock",
        "context_summary":  context_summary,
        "n_items":          len(mcq_df),
        "n_human_students": int(human_df["student_id"].nunique()),
        "n_art_students":   int(crowd_df["student_id"].nunique()),
        "human_rasch":      human_rasch.summary(),
        "art_rasch":        art_rasch.summary(),
        "comparison":       metrics,
        "ai_recommendations": ai_recommendations,
        "human_thetas":     human_thetas,
        "art_thetas":       art_thetas,
    }
    with open(OUTPUTS_DIR / "full_report.json", "w") as f:
        json.dump(report, f, indent=2)

    # ── Final summary ────────────────────────────────────────────────────
    print("\n" + "=" * 55)
    print("  PSYCHOCROWD — PIPELINE COMPLETE")
    print("=" * 55)
    print(f"  Pearson r        : {metrics['pearson_r']:.4f}")
    print(f"  Spearman r       : {metrics['spearman_r']:.4f}")
    print(f"  MAE              : {metrics['mae']:.4f}")
    print(f"  Agreement        : {metrics['interpretation']}")
    print(f"  Outputs saved to : {OUTPUTS_DIR}/")
    print("=" * 55 + "\n")

    return report


if __name__ == "__main__":
    run_pipeline(use_gemini=True)
