import sys
import io
import os
import traceback
import pandas as pd

sys.path.append('.')

from src.mock_solver import MockMCQSolver
from src.profile_generator import build_probability_matrix
from src.crowd_generator import CrowdGenerator
from src.rasch_model import RaschModel
from src.comparator import PsychometricComparator

csv_content = b"question;option_a;option_b;option_c;option_d;correct_option;difficulty_expert\n1+1?;1;2;3;4;B;easy\n2+2?;2;3;4;5;C;medium"

try:
    mcq_df = pd.read_csv(io.BytesIO(csv_content), sep=";", encoding="utf-8")
    print("MCQ DF:\n", mcq_df)
    print("Columns:", mcq_df.columns.tolist())
    
    solver = MockMCQSolver()
    calibrated_df = solver.solve_all(mcq_df)
    print("\nCalibrated DF columns:", calibrated_df.columns.tolist())
    
    prob_matrix = build_probability_matrix(calibrated_df)
    print("Prob matrix shape:", prob_matrix.shape)
    
    crowd_gen = CrowdGenerator(calibrated_df, prob_matrix)
    crowd_gen.generate_crowd()
    art_matrix = crowd_gen.get_response_matrix()
    print("Art matrix shape:", art_matrix.shape)
    
    rasch = RaschModel()
    rasch.fit(art_matrix)
    print("Rasch converged:", rasch.converged)
    
    comp = PsychometricComparator(rasch, rasch, calibrated_df)
    metrics = comp.full_metrics()
    print("Metrics:", metrics)
    print("\n✅ PIPELINE OK!")

except Exception as e:
    print("❌ ERROR:", e)
    traceback.print_exc()
