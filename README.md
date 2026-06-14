# 🎓 PsychoCrowd — AI Psychometric Simulator

**PsychoCrowd** is an AI-powered tool that simulates artificial student crowds for
mathematics MCQ assessments and compares their psychometric behavior to real human
students using the Rasch IRT (Item Response Theory) model. It generates synthetic
student populations with configurable ability profiles and validates how closely
their response patterns match real human test-takers.

The system works out-of-the-box with realistic mock data — no API keys or real datasets
needed. When you're ready, simply drop in your own MCQ bank and human response data,
or enable the Gemini API for real AI-powered item solving. The Rasch model is implemented
from scratch using JMLE (Joint Maximum Likelihood Estimation) for full transparency.

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/your-org/PsychoCrowd.git
cd PsychoCrowd

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Configure API key
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 4. Run the pipeline (mock data, no API needed)
python main.py

# 5. Launch the interactive dashboard
streamlit run dashboard.py
```

---

## 📁 Project Structure

```
PsychoCrowd/
├── .env.example          ← API key template
├── .gitignore
├── README.md
├── requirements.txt
├── config.py             ← All hyperparameters and constants
├── main.py               ← Main pipeline (8-step process)
├── dashboard.py          ← Streamlit interactive dashboard
├── data/
│   ├── mcq_bank.csv      ← Real MCQ file (optional)
│   └── human_responses.csv ← Real human responses (optional)
├── src/
│   ├── __init__.py
│   ├── data_loader.py    ← Load/validate data with mock fallback
│   ├── normalizer.py     ← Math symbol normalization
│   ├── gemini_solver.py  ← Gemini API MCQ solver
│   ├── mock_solver.py    ← Mock solver (no API required)
│   ├── profile_generator.py ← Student profile probabilities
│   ├── crowd_generator.py   ← Artificial student crowd
│   ├── rasch_model.py    ← Rasch 1PL IRT from scratch
│   └── comparator.py     ← Human vs AI comparison + plots
└── outputs/
    ├── response_matrix.csv
    ├── rasch_comparison.csv
    ├── full_report.json
    └── plots/
        ├── scatter_comparison.png
        ├── difficulty_distribution.png
        ├── profile_performance.png
        └── wright_map.png
```

---

## 📊 How to Plug In Real Data

### MCQ Bank (`data/mcq_bank.csv`)

Place a CSV file with these required columns:

| Column              | Type   | Description                    |
|---------------------|--------|--------------------------------|
| `question`          | str    | Problem statement              |
| `option_a`          | str    | Answer choice A                |
| `option_b`          | str    | Answer choice B                |
| `option_c`          | str    | Answer choice C                |
| `option_d`          | str    | Answer choice D                |
| `correct_option`    | str    | One of: A, B, C, D            |
| `difficulty_expert` | str    | One of: easy, medium, hard     |

### Human Responses (`data/human_responses.csv`)

| Column       | Type | Description              |
|--------------|------|--------------------------|
| `student_id` | str  | Unique student identifier|
| `item_id`    | int  | Item index (0-based)     |
| `response`   | int  | 0 = incorrect, 1 = correct |

If either file is missing or malformed, the system automatically falls back
to realistic mock data with a warning.

---

## 🤖 Enable Gemini API

1. Get a free API key at [https://aistudio.google.com](https://aistudio.google.com)
2. Copy `.env.example` to `.env`
3. Add your key: `GEMINI_API_KEY=your_key_here`
4. Run with Gemini: `python main.py` (set `use_gemini=True` in code)

---

## 📈 Expected Outputs

After running the pipeline, the `outputs/` directory will contain:

- **`response_matrix.csv`** — Full artificial student response data
- **`rasch_comparison.csv`** — Item-by-item difficulty comparison
- **`full_report.json`** — Complete metrics report (Pearson r, Spearman r, MAE, etc.)
- **`plots/`** — Publication-ready visualizations:
  - `scatter_comparison.png` — Human vs AI difficulty scatter
  - `difficulty_distribution.png` — KDE overlay of difficulty distributions
  - `profile_performance.png` — Accuracy by student profile
  - `wright_map.png` — Classic Wright person-item map

---

## 📐 Student Profiles

| Profile  | Offset  | Description                     |
|----------|--------|---------------------------------|
| Expert   | +0.20  | Top performers (≈93% on medium) |
| Good     | +0.05  | Above average (≈75% on medium)  |
| Medium   | -0.10  | Average students (≈55% on medium)|
| Weak     | -0.30  | Struggling students (≈30% on medium)|

Each profile generates 50 artificial students (200 total), whose responses
are validated against configurable performance targets.

---

## 📜 License

MIT License — See LICENSE file for details.
