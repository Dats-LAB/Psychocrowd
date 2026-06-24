# Standard Operating Procedure (SOP) - PsychoCrowd V3

## 1. Objectif (Purpose)
PsychoCrowd est un moteur de simulation psychométrique propulsé par l'IA. Son objectif est de simuler des foules d'étudiants artificiels passant des évaluations (QCM de mathématiques) et de comparer leur comportement avec celui d'étudiants humains réels via le modèle de Rasch (IRT 1PL). Cela permet de valider le réalisme des modèles d'IA et de fournir des diagnostics pédagogiques avancés.

## 2. Architecture Technique (V3)
La plateforme a évolué vers une architecture robuste "Full-Stack" :
- **Backend** : FastAPI (Python) gérant l'orchestration, les calculs IRT et les intégrations LLM.
- **Frontend Premium** : Interface React moderne (Vite) avec tableaux de bord interactifs (Plotly/Recharts).
- **Core Engine** : Suite de modules Python (`src/`) pour le traitement statistique et la simulation de Monte Carlo.
- **Modèles d'IA** : Intégration de Google Gemini (Calibration) et DeepSeek (Analyse & Chat).

## 3. Le Pipeline de Traitement (8 Étapes)
PsychoCrowd exécute un flux de travail automatisé :
1. **Chargement** : Lecture des QCM et des réponses humaines (si disponibles).
2. **Normalisation** : Nettoyage des symboles mathématiques et normalisation des colonnes CSV.
3. **Calibration IA** : Le LLM (Gemini) résout les questions, estime la difficulté et identifie les distracteurs.
4. **Matrice de Profils** : Création de 4 profils (Expert, Bon, Moyen, Faible) avec des deltas de performance.
5. **Génération de Foule** : Simulation de 200 étudiants synthétiques.
6. **Modélisation de Rasch (Humain)** : Calcul des paramètres $\theta$ et $b$ sur les données réelles.
7. **Modélisation de Rasch (IA)** : Calcul identique sur les données simulées.
8. **Validation & Comparaison** : Calcul des corrélations de Pearson/Spearman et production du rapport final.

## 4. Fonctionnalités Clés

### 4.1 AI Studio (Interprétation & Rédaction)
Grâce à l'intégration de DeepSeek, la plateforme propose :
- **Interprétation Rasch** : Analyse textuelle détaillée de la convergence et des résultats.
- **Rédaction d'Articles** : Génération d'une section "Résultats" au format académique APA.
- **Chat "PSYCHO"** : Assistant conversationnel expert capable d'analyser les données de la session en cours.

### 4.2 Moteur de Recherche Élève (Pronostics)
- **Compétence Latente** : Mesure du niveau réel ($\theta$) en unités Logit.
- **Prédictions IRT** : Estimation de la probabilité de réussite sur chaque question via la formule logistique de Rasch.
- **Alertes de Risque** : Identification des 5 items les plus critiques pour un élève avec recommandations de remédiation ciblées par domaine (Algèbre, Calcul, Géométrie, etc.).

## 5. Guide d'Utilisation

### Étape 5.1 : Importation
Dans l'onglet **Configuration** :
- Déposez votre banque QCM (`mcq_bank.csv`).
- (Optionnel) Déposez les réponses humaines (`human_responses.csv`).
- Activez l'API Gemini pour une calibration haute fidélité.

### Étape 5.2 : Exécution
Cliquez sur **"Launch Simulation"**. Le backend va orchestrer le pipeline (durée : 1-2 min selon la taille du test).

### Étape 5.3 : Analyse
Naviguez dans les onglets :
- **Item Bank** : Vérifiez la distribution des difficultés.
- **Rasch Model** : Observez la **Wright Map** pour l'alignement personne-item.
- **Validation** : Confirmez la fidélité de la simulation (Pearson $r > 0.85$ recommandé).
- **Student Lookup** : Effectuez un diagnostic individuel.

## 6. Dépannage
- **Erreur de chargement CSV** : Le système accepte les délimiteurs `,` et `;`. Vérifiez l'encodage (UTF-8 conseillé).
- **API Key** : Assurez-vous d'avoir une clé valide pour Gemini (Calibration) et DeepSeek (Studio).
- **Non-convergence** : Si le modèle ne converge pas, augmentez le nombre d'étudiants par profil ou vérifiez la variance de vos données.
