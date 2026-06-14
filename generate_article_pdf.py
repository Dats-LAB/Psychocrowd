"""
PsychoCrowd -- Article de Preparation Doctorale (PDF)
Auteur : Oumaima ELKOULALI
Format : Article academique pour preparation de doctorat
"""

from fpdf import FPDF
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PDF = os.path.join(SCRIPT_DIR, "outputs", "PsychoCrowd_Article_Doctoral.pdf")
os.makedirs(os.path.join(SCRIPT_DIR, "outputs"), exist_ok=True)


class DoctoralPDF(FPDF):
    """Academic-style PDF for doctoral preparation."""

    # Palette
    BLACK = (0, 0, 0)
    DARK = (30, 30, 30)
    BODY = (50, 50, 50)
    GRAY = (100, 100, 100)
    LIGHT_GRAY = (160, 160, 160)
    ACCENT = (0, 51, 102)       # Academic navy
    ACCENT2 = (0, 80, 140)
    RULE = (180, 180, 180)
    WHITE = (255, 255, 255)
    BG_CODE = (245, 245, 245)
    BG_BOX = (240, 245, 255)
    BLUE_LINK = (0, 70, 140)
    RED_ACCENT = (160, 30, 30)

    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.set_auto_page_break(auto=True, margin=28)
        self.set_margins(25, 25, 25)
        self.alias_nb_pages()
        self._is_cover = True

    def header(self):
        if self._is_cover:
            return
        y_top = 12
        self.set_y(y_top)
        # Left: short title
        self.set_font("Times", "I", 8)
        self.set_text_color(*self.GRAY)
        self.cell(80, 5, "PsychoCrowd : Moteur Psychometrique IA", align="L")
        # Right: author & page
        self.cell(0, 5, f"O. ELKOULALI -- Page {self.page_no()}/{{}}", align="R", new_x="LMARGIN", new_y="NEXT")
        # Rule
        self.set_draw_color(*self.RULE)
        self.set_line_width(0.3)
        self.line(25, y_top + 6, self.w - 25, y_top + 6)
        self.set_y(22)

    def footer(self):
        self.set_y(-18)
        self.set_draw_color(*self.RULE)
        self.set_line_width(0.2)
        self.line(25, self.get_y(), self.w - 25, self.get_y())
        self.ln(2)
        self.set_font("Times", "I", 7)
        self.set_text_color(*self.LIGHT_GRAY)
        self.cell(0, 4, "Article de preparation doctorale -- Oumaima ELKOULALI -- Juin 2026", align="C")

    # ---------------------------------------------------------------
    # Cover / Title Page
    # ---------------------------------------------------------------
    def title_page(self):
        self.add_page()
        self._is_cover = True

        # Top decorative rule
        self.set_y(30)
        self.set_draw_color(*self.ACCENT)
        self.set_line_width(1.2)
        self.line(25, 30, self.w - 25, 30)
        self.set_line_width(0.3)
        self.line(25, 32, self.w - 25, 32)

        # Document type
        self.ln(10)
        self.set_font("Times", "I", 12)
        self.set_text_color(*self.ACCENT)
        self.cell(0, 7, "Article de Preparation Doctorale", align="C", new_x="LMARGIN", new_y="NEXT")

        # Title
        self.ln(10)
        self.set_font("Times", "B", 18)
        self.set_text_color(*self.DARK)
        self.multi_cell(0, 10,
            "PsychoCrowd : Un Moteur Psychometrique\n"
            "Pilote par l'Intelligence Artificielle\n"
            "pour l'Evaluation Predictive des\n"
            "Apprentissages en Mathematiques",
            align="C")

        # Decorative thin rule
        self.ln(6)
        self.set_draw_color(*self.ACCENT)
        self.set_line_width(0.5)
        self.line(65, self.get_y(), self.w - 65, self.get_y())

        # Author
        self.ln(10)
        self.set_font("Times", "B", 14)
        self.set_text_color(*self.DARK)
        self.cell(0, 8, "Oumaima ELKOULALI", align="C", new_x="LMARGIN", new_y="NEXT")

        # Affiliation
        self.set_font("Times", "I", 10)
        self.set_text_color(*self.GRAY)
        self.cell(0, 6, "Doctorante en Sciences de l'Education / Intelligence Artificielle", align="C", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 6, "oumaima.elkoulali@recherche.edu", align="C", new_x="LMARGIN", new_y="NEXT")

        # Date
        self.ln(8)
        self.set_font("Times", "", 10)
        self.set_text_color(*self.GRAY)
        self.cell(0, 6, "Juin 2026", align="C", new_x="LMARGIN", new_y="NEXT")

        # Bottom rules
        self.ln(10)
        self.set_draw_color(*self.ACCENT)
        self.set_line_width(0.3)
        self.line(25, self.get_y(), self.w - 25, self.get_y())
        self.set_line_width(1.2)
        self.line(25, self.get_y() + 2, self.w - 25, self.get_y() + 2)

        # Abstract box
        self.ln(12)
        x0 = 25
        y0 = self.get_y()
        box_w = self.w - 50

        self.set_fill_color(*self.BG_BOX)
        self.set_draw_color(*self.ACCENT)
        self.set_line_width(0.4)
        self.rect(x0, y0, box_w, 60, style="DF")

        self.set_xy(x0 + 5, y0 + 4)
        self.set_font("Times", "B", 10)
        self.set_text_color(*self.ACCENT)
        self.cell(box_w - 10, 5, "Resume", new_x="LMARGIN", new_y="NEXT")

        self.set_x(x0 + 5)
        self.set_font("Times", "I", 9)
        self.set_text_color(*self.BODY)
        self.multi_cell(box_w - 10, 4.5,
            "L'evaluation des apprentissages en mathematiques repose traditionnellement sur des indicateurs "
            "statistiques classiques (moyennes, ecarts-types) qui peinent a capturer les interactions entre "
            "competence individuelle et difficulte des items. Cet article presente PsychoCrowd, un outil "
            "open-source combinant la Theorie de Reponse a l'Item (modele de Rasch 1PL), la generation de "
            "foules synthetiques d'etudiants par simulation probabiliste, et les grands modeles de langage "
            "(Google Gemini). Le systeme permet non seulement d'analyser les resultats passes, mais surtout "
            "de predire et pronostiquer la performance future des eleves sur des questions non encore "
            "rencontrees. L'outil se presente sous forme d'un tableau de bord interactif bilingue integrant "
            "un moteur de recommandations pedagogiques individualisees."
        )

        self.set_y(y0 + 50)
        self.set_x(x0 + 5)
        self.set_font("Times", "B", 8)
        self.set_text_color(*self.ACCENT)
        self.cell(20, 4, "Mots-cles : ")
        self.set_font("Times", "I", 8)
        self.set_text_color(*self.BODY)
        self.cell(0, 4, "Psychometrie, IRT, Rasch, IA, Foule Synthetique, Prediction, Gemini, Evaluation Adaptative")

        self._is_cover = False

    # ---------------------------------------------------------------
    # Content helpers
    # ---------------------------------------------------------------
    def section(self, number, title):
        self.ln(6)
        self.set_font("Times", "B", 13)
        self.set_text_color(*self.ACCENT)
        self.cell(0, 7, f"{number}. {title}", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*self.ACCENT)
        self.set_line_width(0.5)
        self.line(25, self.get_y() + 0.5, 85, self.get_y() + 0.5)
        self.ln(4)

    def subsection(self, number, title):
        self.ln(3)
        self.set_font("Times", "B", 11)
        self.set_text_color(*self.ACCENT2)
        self.cell(0, 6, f"{number}  {title}", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def subsubsection(self, number, title):
        self.ln(2)
        self.set_font("Times", "BI", 10)
        self.set_text_color(*self.BODY)
        self.cell(0, 5, f"{number}  {title}", new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def para(self, text, indent=True):
        self.set_font("Times", "", 10)
        self.set_text_color(*self.BODY)
        if indent:
            self.set_x(self.l_margin + 7)
            self.multi_cell(self.w - self.l_margin - self.r_margin - 7, 5.2, text)
        else:
            self.multi_cell(0, 5.2, text)
        self.ln(1.5)

    def bold_para(self, text):
        self.set_font("Times", "B", 10)
        self.set_text_color(*self.DARK)
        self.multi_cell(0, 5.2, text)
        self.ln(1)

    def bullet(self, text, level=0):
        indent = 10 + level * 6
        self.set_x(self.l_margin + indent)
        self.set_font("Times", "", 10)
        self.set_text_color(*self.BODY)
        self.cell(5, 5.2, "-")
        self.multi_cell(0, 5.2, text)
        self.ln(0.8)

    def numbered_item(self, num, text):
        self.set_x(self.l_margin + 10)
        self.set_font("Times", "B", 10)
        self.set_text_color(*self.ACCENT)
        self.cell(8, 5.2, f"{num}.")
        self.set_font("Times", "", 10)
        self.set_text_color(*self.BODY)
        self.multi_cell(0, 5.2, text)
        self.ln(0.8)

    def formula_block(self, text):
        self.ln(3)
        y = self.get_y()
        x = self.l_margin + 20
        w = self.w - 2 * self.l_margin - 40
        self.set_fill_color(*self.BG_BOX)
        self.set_draw_color(*self.ACCENT)
        self.set_line_width(0.3)
        self.rect(x, y, w, 10, style="DF")
        self.set_xy(x, y + 2.5)
        self.set_font("Courier", "B", 10)
        self.set_text_color(*self.ACCENT)
        self.cell(w, 5, text, align="C")
        self.set_y(y + 13)

    def quote_block(self, text):
        self.ln(2)
        x = self.l_margin + 5
        y = self.get_y()
        w = self.w - self.l_margin - self.r_margin - 10
        # Left accent bar
        self.set_fill_color(*self.ACCENT)
        self.rect(x, y, 2.5, 16, style="F")
        # Background
        self.set_fill_color(*self.BG_BOX)
        self.rect(x + 2.5, y, w - 2.5, 16, style="F")
        self.set_xy(x + 7, y + 3)
        self.set_font("Times", "I", 10)
        self.set_text_color(*self.ACCENT2)
        self.multi_cell(w - 12, 5, text)
        self.set_y(y + 19)

    def code_block(self, text):
        self.ln(2)
        x = self.l_margin + 5
        y = self.get_y()
        lines = text.strip().split("\n")
        h = len(lines) * 4.5 + 6
        self.set_fill_color(*self.BG_CODE)
        self.set_draw_color(*self.RULE)
        self.set_line_width(0.2)
        self.rect(x, y, self.w - 2 * self.l_margin - 10, h, style="DF")
        self.set_y(y + 3)
        self.set_font("Courier", "", 8)
        self.set_text_color(*self.DARK)
        for line in lines:
            self.set_x(x + 4)
            self.cell(0, 4.5, line, new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

    def table(self, headers, rows, col_widths=None):
        self.ln(2)
        n_cols = len(headers)
        available = self.w - self.l_margin - self.r_margin
        if col_widths is None:
            col_widths = [available / n_cols] * n_cols

        # Header
        self.set_fill_color(*self.ACCENT)
        self.set_text_color(*self.WHITE)
        self.set_font("Times", "B", 8.5)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, h, border=1, align="C", fill=True)
        self.ln()

        # Rows
        self.set_font("Times", "", 8.5)
        fill = False
        for row in rows:
            if fill:
                self.set_fill_color(245, 248, 252)
            else:
                self.set_fill_color(*self.WHITE)
            self.set_text_color(*self.BODY)
            for i, val in enumerate(row):
                self.cell(col_widths[i], 6.5, str(val), border=1, align="C", fill=True)
            self.ln()
            fill = not fill
        self.ln(3)

    def reference_item(self, num, text):
        self.set_x(self.l_margin + 3)
        self.set_font("Times", "", 8.5)
        self.set_text_color(*self.BODY)
        self.multi_cell(0, 4.5, f"[{num}]  {text}")
        self.ln(1)


def build_pdf():
    pdf = DoctoralPDF()

    # =================================================================
    # PAGE DE TITRE
    # =================================================================
    pdf.title_page()

    # =================================================================
    # TABLE DES MATIERES
    # =================================================================
    pdf.add_page()
    pdf.set_font("Times", "B", 14)
    pdf.set_text_color(*pdf.ACCENT)
    pdf.cell(0, 8, "Table des Matieres", new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(*pdf.ACCENT)
    pdf.set_line_width(0.5)
    pdf.line(25, pdf.get_y() + 1, 80, pdf.get_y() + 1)
    pdf.ln(6)

    toc = [
        ("1", "Introduction et Problematique", "3"),
        ("  1.1", "Les limites de l'evaluation traditionnelle", "3"),
        ("  1.2", "L'apport de la psychometrie moderne", "3"),
        ("  1.3", "Question de recherche", "4"),
        ("2", "Architecture du Systeme", "4"),
        ("  2.1", "Vue d'ensemble du pipeline", "4"),
        ("  2.2", "Description des composants", "5"),
        ("3", "Le Moteur Predictif", "5"),
        ("  3.1", "De l'observation au pronostic", "5"),
        ("  3.2", "Classification automatique des domaines", "6"),
        ("4", "Le Role de l'Intelligence Artificielle", "6"),
        ("  4.1", "Google Gemini comme agent evaluateur", "6"),
        ("  4.2", "Systeme de cache intelligent", "7"),
        ("  4.3", "Analyse des erreurs", "7"),
        ("5", "La Foule Synthetique", "7"),
        ("6", "Validation Psychometrique", "8"),
        ("7", "Interface Utilisateur", "8"),
        ("8", "Guide d'Utilisation", "9"),
        ("9", "Cas d'Usage Concrets", "9"),
        ("10", "Limites et Perspectives", "10"),
        ("11", "Conclusion", "10"),
        ("", "References bibliographiques", "11"),
    ]

    for num, title, page in toc:
        is_main = not num.startswith("  ")
        pdf.set_font("Times", "B" if is_main else "", 10 if is_main else 9)
        pdf.set_text_color(*pdf.DARK if is_main else pdf.GRAY)
        indent = 0 if is_main else 10
        pdf.set_x(pdf.l_margin + indent)
        title_w = pdf.w - pdf.l_margin - pdf.r_margin - indent - 10
        pdf.cell(title_w, 5.5, f"{num}  {title}" if num.strip() else title)
        pdf.set_font("Times", "", 9)
        pdf.cell(10, 5.5, page, align="R", new_x="LMARGIN", new_y="NEXT")
        if is_main:
            pdf.ln(0.5)

    # =================================================================
    # SECTION 1 -- INTRODUCTION
    # =================================================================
    pdf.add_page()
    pdf.section("1", "Introduction et Problematique")

    pdf.subsection("1.1", "Les limites de l'evaluation traditionnelle")
    pdf.para(
        "Dans le systeme educatif contemporain, l'evaluation d'un examen de mathematiques se resume "
        "trop souvent a un score brut : << 14/20 >>. Ce chiffre unique, bien qu'intuitif pour le grand "
        "public, masque des informations essentielles pour le diagnostic pedagogique et la prise de "
        "decision educative."
    )
    pdf.para("Trois limites majeures peuvent etre identifiees :")
    pdf.bullet(
        "Incommensurabilite : Un 14/20 sur un examen facile n'a pas la meme valeur qu'un 14/20 sur "
        "un examen difficile. Les scores bruts ne sont pas comparables d'un test a l'autre, d'une "
        "cohorte a l'autre, ni d'une annee a l'autre."
    )
    pdf.bullet(
        "Masquage des profils heterogenes : Deux eleves obtenant un score identique peuvent presenter "
        "des profils de competences radicalement differents. L'un excelle en algebre et echoue en "
        "geometrie ; l'autre presente le schema inverse."
    )
    pdf.bullet(
        "Absence de capacite predictive : Le score ne predit rien. Savoir qu'un eleve a obtenu 14/20 "
        "ne nous indique ni s'il reussira la prochaine evaluation, ni quelles sont les questions "
        "precises ou il risque d'echouer."
    )
    pdf.para(
        "Ces limitations motivent le recours a des cadres theoriques plus sophistiques, capables de "
        "modeliser simultanement les caracteristiques des items (questions) et des personnes (eleves)."
    )

    pdf.subsection("1.2", "L'apport de la psychometrie moderne")
    pdf.para(
        "La psychometrie -- science de la mesure des aptitudes et des traits latents -- apporte une "
        "reponse rigoureuse a ces limites grace a la Theorie de Reponse a l'Item (Item Response Theory, "
        "IRT). Le modele fondateur de cette theorie, propose par Georg Rasch (1960), postule que la "
        "probabilite qu'un sujet i reponde correctement a un item j depend exclusivement de deux "
        "parametres latents :"
    )

    pdf.formula_block("P(X_ij = 1) = 1 / (1 + exp(-(theta_i - b_j)))")

    pdf.para("ou :")
    pdf.bullet("theta_i represente la competence latente du sujet i, exprimee en logits ;")
    pdf.bullet("b_j represente la difficulte latente de l'item j, egalement en logits.")
    pdf.para(
        "Ce modele possede une propriete remarquable dite d'objectivite specifique (Rasch, 1960) : "
        "lorsque theta_i = b_j, le sujet a exactement 50% de probabilite de repondre correctement. "
        "Lorsque theta_i > b_j, cette probabilite depasse 50% ; lorsque theta_i < b_j, elle tombe "
        "en dessous. Cette propriete permet une mesure invariante, independante de l'echantillon "
        "d'items et de personnes utilise pour le calibrage."
    )

    pdf.subsection("1.3", "Question de recherche")
    pdf.para("Le present travail s'articule autour de la question de recherche suivante :")
    pdf.quote_block(
        "Peut-on combiner l'intelligence artificielle generative, la simulation de foules synthetiques "
        "et le modele de Rasch pour predire la performance individuelle d'un eleve sur des items non encore administres ?"
    )
    pdf.para(
        "Nous montrons dans cet article que la reponse est affirmative, en presentant PsychoCrowd, "
        "un outil integrant ces trois paradigmes dans un systeme unifie."
    )

    # =================================================================
    # SECTION 2 -- ARCHITECTURE
    # =================================================================
    pdf.section("2", "Architecture du Systeme")

    pdf.subsection("2.1", "Vue d'ensemble du pipeline")
    pdf.para(
        "PsychoCrowd repose sur une architecture modulaire en pipeline sequentiel composee de huit "
        "etapes. Chaque composant est encapsule dans un module Python independant, favorisant la "
        "maintenabilite, la testabilite et l'extensibilite du systeme. Le diagramme suivant illustre "
        "le flux de traitement :"
    )
    pdf.code_block(
        " [1] Data Loader  -->  [2] Normalizer  -->  [3] AI Solver  -->  [4] Prob. Matrix\n"
        "      (CSV)           (Math Symbols)        (Gemini API)       (4 profils)\n"
        "                                                                    |\n"
        " [8] JSON Report  <-- [7] Comparator  <-- [6] Rasch JMLE  <-- [5] Crowd Gen.\n"
        "    (full_report)      (Validation)        (theta, b)        (N etudiants)"
    )
    pdf.para(
        "Le pipeline est executable soit en ligne de commande (python main.py), soit via le tableau "
        "de bord interactif Streamlit (streamlit run dashboard.py). Dans les deux cas, les resultats "
        "sont persistes dans le repertoire outputs/ sous forme de fichiers CSV et JSON."
    )

    pdf.subsection("2.2", "Description des composants logiciels")

    pdf.table(
        ["Module", "Fichier source", "Responsabilite"],
        [
            ["Data Loader", "data_loader.py", "Parsing CSV, classification par domaine"],
            ["Normalizer", "normalizer.py", "Normalisation symboles mathematiques Unicode"],
            ["AI Solver", "gemini_solver.py", "Resolution QCM via Gemini + cache persistant"],
            ["Profile Gen.", "profile_generator.py", "Matrice P(succes | profil, difficulte)"],
            ["Crowd Gen.", "crowd_generator.py", "Echantillonnage Bernoulli de N etudiants"],
            ["Rasch Model", "rasch_model.py", "JMLE 1PL + Newton-Raphson (estimate_ability)"],
            ["Comparator", "comparator.py", "Pearson, Spearman, MAE, RMSE, graphiques"],
            ["Dashboard", "dashboard.py", "Interface Streamlit, 7 onglets, bilingue FR/EN"],
        ],
        col_widths=[28, 34, 98]
    )

    # =================================================================
    # SECTION 3 -- MOTEUR PREDICTIF
    # =================================================================
    pdf.section("3", "Le Moteur Predictif")

    pdf.subsection("3.1", "De l'observation au pronostic")
    pdf.para(
        "Un correcteur automatique se contente de confronter les reponses des eleves a un corrige "
        "pour produire un score. PsychoCrowd va significativement plus loin en estimant un trait "
        "latent -- la competence theta -- et en l'exploitant pour predire la performance future de "
        "l'eleve. Le processus predictif se decompose en quatre etapes :"
    )
    pdf.bold_para("Etape 1 : Calibration du test (estimation des difficultes b_j)")
    pdf.para(
        "Le modele de Rasch 1PL est ajuste sur l'ensemble des donnees disponibles (humaines et/ou "
        "synthetiques) par la methode d'estimation par maximum de vraisemblance jointe (Joint Maximum "
        "Likelihood Estimation, JMLE). Ce processus iteratif produit simultanement les estimations "
        "des difficultes latentes b_j de chaque item et des competences theta_i de chaque sujet."
    )
    pdf.bold_para("Etape 2 : Estimation de la competence individuelle (Newton-Raphson)")
    pdf.para(
        "Pour un nouveau sujet ou un sujet isole, l'algorithme de Newton-Raphson estime sa competence "
        "latente theta en maximisant la vraisemblance conditionnelle de ses reponses observees, "
        "etant donne les difficultes b_j prealablement calibrees :"
    )
    pdf.formula_block("theta_{k+1} = theta_k + (r - E[r|theta_k]) / I(theta_k)")
    pdf.para(
        "ou r est le score brut observe, E[r|theta_k] le score attendu sous le modele, et I(theta_k) "
        "l'information de Fisher. La convergence est typiquement atteinte en moins de 20 iterations "
        "avec une tolerance de 10^-6."
    )
    pdf.bold_para("Etape 3 : Prediction probabiliste item par item")
    pdf.para(
        "Une fois theta_i estime, la probabilite de reussite du sujet i sur n'importe quel item j "
        "de la banque -- y compris ceux qu'il n'a pas encore passes -- est calculee par application "
        "directe de la fonction de reponse a l'item (ICC) :"
    )
    pdf.formula_block("P_hat(X_ij = 1) = 1 / (1 + exp(-(theta_i - b_j)))")

    pdf.bold_para("Etape 4 : Pronostic d'echecs et recommandations ciblees")
    pdf.para(
        "Les items presentant les plus faibles probabilites de reussite predites sont signales comme "
        "<< zones a risque >>. PsychoCrowd les classe par ordre croissant de probabilite et formule "
        "des recommandations pedagogiques adaptees au domaine mathematique concerne (cf. section 3.2)."
    )

    pdf.subsection("3.2", "Classification automatique des domaines mathematiques")
    pdf.para(
        "PsychoCrowd implemente un classificateur lexical qui categorise automatiquement chaque item "
        "dans l'un des cinq domaines suivants, par analyse des mots-cles presents dans l'enonce :"
    )
    pdf.table(
        ["Domaine", "Indicateurs lexicaux", "Exemple de remediation"],
        [
            ["Calculus", "derivee, integrale, limite", "Regles de derivation en cascade"],
            ["Complex Numbers", "module, argument, exp.", "Representations geometriques"],
            ["Algebra", "factorisation, equation", "Identites remarquables"],
            ["Geometry", "aire, perimetre, distance", "Formules d'aires classiques"],
            ["Arithmetic", "fraction, PGCD, divisibilite", "Priorites operatoires"],
        ],
        col_widths=[32, 45, 83]
    )

    # =================================================================
    # SECTION 4 -- ROLE DE L'IA
    # =================================================================
    pdf.section("4", "Le Role de l'Intelligence Artificielle")

    pdf.subsection("4.1", "Google Gemini comme agent evaluateur")
    pdf.para(
        "L'une des contributions originales de PsychoCrowd est l'utilisation d'un grand modele de "
        "langage (Large Language Model, LLM) -- en l'occurrence Google Gemini -- non pas comme un "
        "simple assistant conversationnel, mais comme un agent evaluateur dont le comportement de "
        "resolution est systematiquement compare a celui des etudiants humains."
    )
    pdf.para("Pour chaque item QCM, Gemini est invite a produire deux informations :")
    pdf.numbered_item(1, "La reponse selectionnee (A, B, C ou D) ;")
    pdf.numbered_item(2,
        "Un indice de confiance auto-rapporte (de 0.0 a 1.0), qui constitue un proxy de la "
        "difficulte percue par le modele."
    )
    pdf.para(
        "L'indice de confiance s'avere particulierement informatif : une confiance basse (< 0.50) "
        "signale que meme un modele performant juge l'item << difficile >>, ce qui correle "
        "significativement avec les taux d'echec observes chez les sujets humains. Cette correlation "
        "ouvre des perspectives interessantes pour la pre-calibration automatique des banques d'items."
    )

    pdf.subsection("4.2", "Systeme de cache persistant")
    pdf.para(
        "Les appels a l'API Gemini etant couteux en temps (latence reseau) et en quota (limitation "
        "de debit), PsychoCrowd implemente un mecanisme de cache persistant base sur une cle composite "
        "unique par item :"
    )
    pdf.code_block(
        "cle = hash(question + \"##\" + opt_A + \"##\" + opt_B + \"##\" + opt_C + \"##\" + opt_D)"
    )
    pdf.para(
        "Le cache est serialise au format JSON (data/gemini_cache.json) et sauvegarde incrementalement "
        "apres chaque nouvelle resolution. En pratique, la premiere simulation d'une banque de 1000 items "
        "requiert environ 45 minutes (en raison des limites de quota), mais toute simulation ulterieure "
        "sur les memes items s'execute en moins d'une seconde."
    )

    pdf.subsection("4.3", "Analyse qualitative des erreurs")
    pdf.para(
        "Au-dela de la resolution des items, Gemini est mobilise pour produire une analyse qualitative "
        "des erreurs les plus frequentes. Pour les 5 items presentant les taux d'echec les plus eleves, "
        "le systeme soumet a Gemini le contexte complet de l'erreur (reponse correcte, distracteur le "
        "plus choisi) et sollicite une explication pedagogique de la misconception sous-jacente. Ces "
        "recommandations sont affichees dans l'onglet << Recommandations IA >> du tableau de bord."
    )

    # =================================================================
    # SECTION 5 -- FOULE SYNTHETIQUE
    # =================================================================
    pdf.section("5", "La Foule Synthetique")

    pdf.para(
        "Dans de nombreux contextes educatifs, les donnees d'etudiants reels sont limitees : petits "
        "effectifs, classes heterogenes, absence de donnees historiques. La generation d'une foule "
        "synthetique permet de calibrer le modele de Rasch en l'absence de donnees humaines suffisantes, "
        "et de valider le realisme du calibrage par comparaison croisee."
    )
    pdf.para(
        "PsychoCrowd modelise quatre profils d'etudiants avec des taux de reussite cibles differencies "
        "selon le niveau de difficulte des items :"
    )

    pdf.table(
        ["Profil", "Items faciles", "Items moyens", "Items difficiles"],
        [
            ["Expert", "~98%", "~93%", "~82%"],
            ["Good", "~90%", "~77%", "~55%"],
            ["Medium", "~75%", "~55%", "~30%"],
            ["Weak", "~55%", "~30%", "~12%"],
        ],
        col_widths=[35, 40, 43, 42]
    )

    pdf.para(
        "Chaque reponse simulee est generee par un tirage de Bernoulli independant : "
        "X_ij ~ Bernoulli(p_ij), ou p_ij est la probabilite conditionnelle associee au profil du "
        "sujet i et a la difficulte de l'item j. Par defaut, le systeme genere 50 etudiants par profil, "
        "soit 200 etudiants artificiels au total."
    )

    # =================================================================
    # SECTION 6 -- VALIDATION
    # =================================================================
    pdf.section("6", "Validation Psychometrique")

    pdf.para(
        "La validite du systeme repose sur la comparaison des parametres de difficulte b_j estimes "
        "par le modele de Rasch sur deux populations independantes : les etudiants humains (donnees "
        "reelles) et les etudiants artificiels (foule synthetique). Les metriques suivantes sont "
        "calculees :"
    )

    pdf.table(
        ["Metrique", "Definition formelle", "Seuil << Excellent >>"],
        [
            ["Pearson r", "Correlation lineaire b_hum vs b_art", "> 0.90"],
            ["Spearman rho", "Correlation de rang (robuste)", "> 0.85"],
            ["MAE", "Erreur absolue moyenne (logits)", "< 0.50"],
            ["RMSE", "Racine de l'erreur quadratique moyenne", "< 0.75"],
        ],
        col_widths=[30, 72, 58]
    )

    pdf.para("Trois visualisations standardisees sont generees automatiquement :")
    pdf.bullet(
        "Scatter plot : representation des difficultes humaines (abscisse) vs. artificielles (ordonnee). "
        "La proximite des points a la droite y = x indique un bon accord."
    )
    pdf.bullet(
        "Distributions KDE : superposition des estimations de densite par noyau des deux populations. "
        "Des courbes similaires temoignent du realisme de la simulation."
    )
    pdf.bullet(
        "Carte de Wright : representation standard en psychometrie placant les personnes (gauche) et "
        "les items (droite) sur une echelle commune en logits. Un alignement indique une probabilite "
        "de reussite de 50%."
    )

    # =================================================================
    # SECTION 7 -- INTERFACE
    # =================================================================
    pdf.section("7", "Interface Utilisateur")

    pdf.para(
        "PsychoCrowd se materialise sous la forme d'un tableau de bord interactif construit avec "
        "le framework Streamlit (Python). L'interface est integralement bilingue (francais/anglais) "
        "et s'organise en sept onglets thematiques :"
    )

    pdf.table(
        ["Onglet", "Fonction principale"],
        [
            ["Banque d'Items", "Apercu des items, distribution de difficulte, donut chart"],
            ["Foule Synthetique", "Heatmap des reponses, precision par profil"],
            ["Moteur Rasch", "Parametres IRT (theta, b), carte de Wright"],
            ["Validation", "Correlations, scatter plot, distributions KDE"],
            ["Recherche Eleve", "Profil individuel, predictions, pronostic d'echecs"],
            ["Recommandations IA", "Analyse des erreurs par Gemini, conseils pedagogiques"],
            ["Centre d'Aide", "Tutoriel guide en 4 etapes (de A a Z)"],
        ],
        col_widths=[38, 122]
    )

    pdf.para(
        "Le design adopte une esthetique premium : typographie Inter (Google Fonts), palette de "
        "couleurs harmonisee (degrades bleu profond, accents turquoise), cartes interactives avec "
        "animations de survol, et composants glassmorphism (arriere-plan semi-transparent avec flou)."
    )

    # =================================================================
    # SECTION 8 -- GUIDE D'UTILISATION
    # =================================================================
    pdf.section("8", "Guide d'Utilisation")

    pdf.subsection("8.1", "Prerequis techniques")
    pdf.code_block(
        "Python >= 3.9\n"
        "pip install streamlit pandas numpy scipy plotly matplotlib seaborn\n"
        "pip install google-generativeai  # optionnel, pour le solver IA"
    )

    pdf.subsection("8.2", "Lancement")
    pdf.code_block(
        "# Interface interactive\n"
        "streamlit run dashboard.py\n"
        "\n"
        "# Pipeline en ligne de commande\n"
        "python main.py"
    )

    pdf.subsection("8.3", "Format des donnees d'entree")
    pdf.bold_para("Banque QCM (mcq_bank.csv) -- optionnel :")
    pdf.code_block(
        "Question;Choice_A;Choice_B;Choice_C;Choice_D;Correct_Answer;Difficulty\n"
        "Derivee de f(x)=x^3 ?;x^2;2x^2;3x^2;3x;C;Medium"
    )
    pdf.bold_para("Reponses humaines (human_responses.csv) -- optionnel :")
    pdf.code_block(
        "student_id,item_id,response\n"
        "Eleve_1,0,1\n"
        "Eleve_1,1,0"
    )

    pdf.subsection("8.4", "Fichiers de sortie")
    pdf.table(
        ["Fichier", "Contenu"],
        [
            ["outputs/full_report.json", "Rapport integral (Rasch, validation, thetas, reco.)"],
            ["outputs/response_matrix.csv", "Matrice de reponses de la foule synthetique"],
            ["outputs/rasch_comparison.csv", "Comparaison item par item des difficultes"],
            ["plots/wright_map.png", "Carte de Wright (personnes vs. items)"],
            ["plots/scatter_comparison.png", "Nuage de points de validation croisee"],
        ],
        col_widths=[62, 98]
    )

    # =================================================================
    # SECTION 9 -- CAS D'USAGE
    # =================================================================
    pdf.section("9", "Cas d'Usage Concrets")

    pdf.subsection("9.1", "Pour l'enseignant")
    pdf.para(
        "Un professeur de mathematiques en classe de terminale souhaite analyser les resultats de "
        "son dernier controle (30 QCM, 35 eleves). Il importe ses deux fichiers CSV dans PsychoCrowd "
        "et obtient : (a) la competence latente theta de chaque eleve, comparable d'un test a l'autre ; "
        "(b) les items les plus mal calibres ; (c) pour chaque eleve, une prediction de reussite sur "
        "les items non administres, permettant de preparer une remediation ciblee."
    )

    pdf.subsection("9.2", "Pour le concepteur d'evaluations")
    pdf.para(
        "Un responsable pedagogique souhaite valider la qualite d'une banque de 1000 QCM avant "
        "deploiement dans un examen national. PsychoCrowd genere la foule synthetique, calibre le "
        "modele de Rasch, et identifie les items problematiques (overfit/underfit selon l'infit MNSQ), "
        "les domaines sous-representes, et les distracteurs revelant des misconceptions systematiques."
    )

    pdf.subsection("9.3", "Pour le chercheur en sciences de l'education")
    pdf.para(
        "Un chercheur souhaite comparer la perception de difficulte d'un LLM avec celle de sujets "
        "humains. PsychoCrowd fournit directement les correlations et visualisations necessaires, "
        "sans necessite d'ecrire du code supplementaire."
    )

    # =================================================================
    # SECTION 10 -- LIMITES ET PERSPECTIVES
    # =================================================================
    pdf.section("10", "Limites et Perspectives")

    pdf.subsection("10.1", "Limites identifiees")
    pdf.bullet(
        "Modele 1PL uniquement : le modele actuel ne prend en compte ni la discrimination des items "
        "(parametre a du 2PL) ni le pseudo-guessing (parametre c du 3PL)."
    )
    pdf.bullet(
        "Classification lexicale heuristique : la categorisation par mots-cles peut mal classifier "
        "des items a enonce ambigu. Un classificateur par apprentissage supervise serait plus robuste."
    )
    pdf.bullet(
        "Dependance a l'API Gemini : le solver IA necessite un acces reseau et une cle API. Le mode "
        "mock permet de contourner cette dependance, mais les recommandations ne sont alors pas generees."
    )

    pdf.subsection("10.2", "Perspectives de developpement")
    pdf.bullet("Extension aux modeles 2PL et 3PL pour ameliorer la precision de la mesure.")
    pdf.bullet(
        "Implementation d'un module de Testing Adaptatif Informatise (CAT) selectionnant dynamiquement "
        "les items maximisant l'information de Fisher a chaque etape."
    )
    pdf.bullet("Generalisation multi-disciplinaire : physique, chimie, biologie.")
    pdf.bullet(
        "Tableau de bord collaboratif permettant le partage de banques d'items entre enseignants "
        "et la comparaison inter-classes."
    )

    # =================================================================
    # SECTION 11 -- CONCLUSION
    # =================================================================
    pdf.section("11", "Conclusion")
    pdf.para(
        "PsychoCrowd represente une convergence originale entre trois domaines : la psychometrie "
        "classique (modele de Rasch 1PL), la simulation computationnelle (foules synthetiques par "
        "echantillonnage de Bernoulli), et l'intelligence artificielle generative (Google Gemini). "
        "L'outil depasse le paradigme du simple correcteur automatique pour s'inscrire dans une "
        "logique de mesure, prediction et recommandation."
    )
    pdf.para(
        "En estimant la competence latente de chaque apprenant et en appliquant la fonction de reponse "
        "a l'item a l'ensemble de la banque de questions, PsychoCrowd transforme une simple matrice de "
        "reponses binaires en un portrait psychometrique dynamique, capable de pronostiquer les succes "
        "et les echecs futurs, item par item, domaine par domaine."
    )
    pdf.para(
        "Pour l'enseignant, il constitue un outil de diagnostic et de remediation. Pour le concepteur "
        "d'evaluations, un laboratoire de calibration. Pour le chercheur en sciences de l'education, "
        "une plateforme d'experimentation reproductible. Pour l'apprenant, enfin, il porte -- "
        "indirectement -- la promesse d'un accompagnement plus personnalise, plus equitable, et "
        "davantage fonde sur des donnees probantes."
    )

    # =================================================================
    # REFERENCES BIBLIOGRAPHIQUES
    # =================================================================
    pdf.ln(4)
    pdf.section("", "References Bibliographiques")

    refs = [
        ("Rasch, G. (1960). Probabilistic Models for Some Intelligence and Attainment Tests. "
         "Copenhagen : Danish Institute for Educational Research."),
        ("Wright, B. D. et Stone, M. H. (1979). Best Test Design: Rasch Measurement. "
         "Chicago : MESA Press."),
        ("Linacre, J. M. (2002). What do Infit and Outfit, Mean-square and Standardized mean? "
         "Rasch Measurement Transactions, 16(2), 878."),
        ("De Ayala, R. J. (2009). The Theory and Practice of Item Response Theory. "
         "New York : Guilford Press."),
        ("Baker, F. B. et Kim, S.-H. (2004). Item Response Theory: Parameter Estimation Techniques. "
         "New York : Marcel Dekker. 2e edition."),
        ("Lord, F. M. (1980). Applications of Item Response Theory to Practical Testing Problems. "
         "Hillsdale, NJ : Lawrence Erlbaum Associates."),
        ("Hambleton, R. K., Swaminathan, H. et Rogers, H. J. (1991). Fundamentals of Item Response "
         "Theory. Newbury Park, CA : Sage."),
        ("Google DeepMind (2024). Gemini: A Family of Highly Capable Multimodal Models. "
         "Technical Report, arXiv:2312.11805."),
        ("Embretson, S. E. et Reise, S. P. (2000). Item Response Theory for Psychologists. "
         "Mahwah, NJ : Lawrence Erlbaum Associates."),
        ("van der Linden, W. J. et Glas, C. A. W. (2010). Elements of Adaptive Testing. "
         "New York : Springer."),
    ]

    for i, ref in enumerate(refs, 1):
        pdf.reference_item(i, ref)

    # =================================================================
    # SAVE
    # =================================================================
    pdf.output(OUTPUT_PDF)
    size_kb = os.path.getsize(OUTPUT_PDF) / 1024
    print(f"\n{'='*60}")
    print(f"  PDF DOCTORAL genere avec succes !")
    print(f"  Auteur   : Oumaima ELKOULALI")
    print(f"  Chemin   : {OUTPUT_PDF}")
    print(f"  Taille   : {size_kb:.0f} Ko")
    print(f"  Pages    : {pdf.page_no()}")
    print(f"{'='*60}\n")
    return OUTPUT_PDF


if __name__ == "__main__":
    build_pdf()
