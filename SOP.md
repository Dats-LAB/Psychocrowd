# Standard Operating Procedure (SOP) - PsychoCrowd

## 1. Objectif (Purpose)
PsychoCrowd est un moteur psychométrique propulsé par l'IA. Son objectif est de simuler des foules d'étudiants artificiels passant des évaluations sous forme de QCM de mathématiques, et de comparer leur comportement psychométrique avec celui d'étudiants humains réels en utilisant le modèle de Rasch (IRT 1PL).

## 2. Prérequis (Prerequisites)
- Environnement Python 3.9+
- Dépendances installées : `pip install -r requirements.txt` (inclut Streamlit, Pandas, Numpy, Plotly, etc.)
- (Optionnel) Une clé API Google Gemini si vous souhaitez utiliser l'IA générative pour résoudre les questions au lieu du solveur par défaut (Mock).

## 3. Préparation des Données (Data Preparation)
Pour utiliser vos propres données, préparez deux fichiers CSV :
1. **Banque QCM (`mcq_bank.csv`)** : Doit contenir au minimum les colonnes `item_id`, `question`, `option_a`, `option_b`, `option_c`, `option_d`, `correct_option` (A, B, C, ou D), et `difficulty_expert` (easy, medium, hard).
2. **Réponses Humaines (`human_responses.csv`)** : Doit contenir les colonnes `student_id`, `item_id`, et `response` (1 pour juste, 0 pour faux).

*Note : Si aucun fichier n'est fourni, PsychoCrowd générera automatiquement des données fictives pour vous permettre de tester l'outil.*

## 4. Procédure d'Utilisation (Step-by-Step Workflow)

### Étape 4.1 : Lancement de l'Interface
Ouvrez un terminal, placez-vous dans le dossier du projet et exécutez :
```bash
streamlit run dashboard.py
```
Ouvrez ensuite le lien local dans votre navigateur (généralement `http://localhost:8501`).

### Étape 4.2 : Importation
Dans la barre latérale gauche (Sidebar) :
- Glissez-déposez votre fichier de QCM dans "Banque QCM (CSV)".
- Glissez-déposez vos réponses d'élèves dans "Réponses Humaines (CSV)".

### Étape 4.3 : Configuration de l'IA
- Réglez le "Nombre d'étudiants par profil" (par défaut : 10). Cela déterminera la taille de la foule synthétique générée.
- Activez "Google Gemini API" si vous possédez une clé API, sinon laissez l'option désactivée pour utiliser la simulation locale ultrarapide.

### Étape 4.4 : Exécution
Cliquez sur le bouton **"🚀 LANCER LA SIMULATION"**. 
Attendez que l'indicateur de progression disparaisse. L'opération prend généralement entre 5 et 15 secondes.

## 5. Analyse des Résultats (Analyzing Results)
Naviguez à travers les onglets du tableau de bord :
- **Banque d'Items** : Vérifiez que vos questions ont été correctement importées et classées.
- **Foule Synthétique** : Observez la matrice de réponse générée par l'IA et vérifiez que les profils (Expert, Bon, Moyen, Faible) respectent les probabilités de réussite attendues.
- **Moteur Rasch** : Vérifiez la "Convergence" du modèle (qui doit être à "Oui"). Analysez la Carte de Wright pour voir l'alignement entre la difficulté des questions et le niveau des élèves.
- **Validation** : Vérifiez la corrélation de Pearson et de Spearman. Un coefficient > 0.8 indique une excellente concordance entre le comportement humain et artificiel.
- **Recherche Élève** : Utilisez cet onglet pour faire un audit granulaire sur un étudiant spécifique (humain ou artificiel) et voir ses réponses item par item.

## 6. Dépannage (Troubleshooting)
- **Erreur de chargement CSV** : Vérifiez que vos fichiers CSV utilisent bien la virgule `,` comme séparateur et respectent strictement le nom des colonnes requises.
- **Modèle Rasch non convergent** : Cela arrive si les données sont trop extrêmes (étudiants qui ont 100% ou 0%). L'algorithme applique une correction, mais assurez-vous d'avoir une variance suffisante dans vos données réelles.
- **Boutons inactifs** : Assurez-vous que le serveur Streamlit tourne toujours dans le terminal de fond.
