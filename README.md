# 🎓 PsychoCrowd — AI Psychometric Simulator (V3)

**PsychoCrowd** is an AI-powered tool that simulates artificial student crowds for
mathematics MCQ assessments and compares their psychometric behavior to real human
students using the Rasch IRT (Item Response Theory) model.

The system now features a robust **Full-Stack V3 architecture** with a FastAPI backend and a React (Vite) premium dashboard.

---

## 🚀 Quick Start (V3 Premium)

### 1. Setup Backend
```bash
# Install dependencies
pip install -r requirements.txt

# Configure API keys in .env
cp .env.example .env
# Edit .env and add GEMINI_API_KEY and DEEPSEEK_API_KEY

# Start the API server
uvicorn api.app:app --host 0.0.0.0 --port 8000
```

### 2. Setup Frontend
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) to access the premium dashboard.

---

## 📊 Alternate Interfaces

### Streamlit Dashboard
For a lightweight, single-process experience:
```bash
streamlit run dashboard.py
```

### CLI Pipeline
To run the analysis directly from the terminal:
```bash
python main.py
```

---

## 📁 Project Structure

```
PsychoCrowd/
├── api/                  ← FastAPI Backend (V3 Gateway)
├── frontend/             ← React/Vite Premium Dashboard
├── src/                  ← Core Psychometric Engine
│   ├── rasch_model.py    ← JMLE Rasch Implementation
│   ├── gemini_solver.py  ← Gemini API Integration
│   └── crowd_generator.py ← Monte Carlo Crowd Simulation
├── data/                 ← Input CSVs & Caches
├── outputs/              ← Generated Reports & Plots
├── main.py               ← Standard Pipeline Execution
├── dashboard.py          ← Streamlit Interface
└── config.py             ← Global Configuration
```

---

## 📐 Key Features
- **8-Step Pipeline**: From MCQ loading to Psychometric Validation.
- **AI Studio**: DeepSeek-powered interpretations, article drafting, and analytical chat.
- **Student Lookup**: IRT-based success forecasts and personalized remediation.
- **Rasch JMLE**: Native implementation of the 1-Parameter Logistic model.

---

## 📜 License
MIT License — See LICENSE file for details.
