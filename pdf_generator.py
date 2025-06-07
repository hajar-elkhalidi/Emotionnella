from fpdf import FPDF
import tempfile
import os
import uuid

# --- PDF Generator class ---
class PDF(FPDF):
    def __init__(self):
        super().__init__()
        # Ajouter une police Unicode personnalisée
        self.add_font('DejaVu', '', 'fonts/DejaVuSans.ttf', uni=True)
        self.add_font('DejaVu', 'B', 'fonts/DejaVuSans-Bold.ttf', uni=True)
        self.set_font('DejaVu', 'B', 16)
    
    # Ajout d'une méthode pour gérer les cellules multilignes avec texte long
    def multi_cell_with_wrap(self, w, h, txt, border=0, align='L', fill=False):
        # Enregistrer la position x de départ
        x_start = self.get_x()
        # Définir une taille de police plus petite pour le texte qui risque d'être trop long
        current_font = self.font_family
        current_style = self.font_style
        current_size = self.font_size
        self.set_font(current_font, current_style, 9)
        
        # Appeler multi_cell pour le texte qui pourrait être long
        self.multi_cell(w, h, txt, border, align, fill)
        
        # Retourner à la position X de départ, mais à la nouvelle position Y
        self.set_xy(x_start + w, self.get_y() - h if self.get_y() > h else 0)
        
        # Rétablir la police d'origine
        self.set_font(current_font, current_style, current_size)

def generer_pdf(df, fig1, fig2, fig3=None, profil_df=None, top_students_dict=None):
    temp_dir = tempfile.gettempdir()
    file1_path = os.path.join(temp_dir, f"{uuid.uuid4()}.png")
    file2_path = os.path.join(temp_dir, f"{uuid.uuid4()}.png")
    file3_path = os.path.join(temp_dir, f"{uuid.uuid4()}.png") if fig3 is not None else None

    fig1.write_image(file1_path)
    fig2.write_image(file2_path)
    if fig3 is not None:
        fig3.write_image(file3_path)

    pdf = PDF()
    pdf.add_page()
    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(200, 10, "Rapport Émotionnella", ln=True, align="C")

    pdf.set_font("DejaVu", "", 12)
    pdf.ln(10)
    pdf.cell(200, 10, f"Nombre total d'étudiants : {len(df)}", ln=True)

    pdf.image(file1_path, w=180)
    pdf.add_page()
    pdf.image(file2_path, w=180)
    
    if fig3 is not None:
        pdf.add_page()
        pdf.image(file3_path, w=180)
    
    # Ajouter le tableau des profils de clusters au PDF
    if profil_df is not None:
        pdf.add_page()
        pdf.set_font("DejaVu", "B", 14)
        pdf.cell(200, 10, "Profil des Clusters", ln=True)
        pdf.ln(5)

        # Largeurs des colonnes
        col_widths = [45, 25, 25, 30, 55]
        row_height = 6

        # En-têtes du tableau
        pdf.set_font("DejaVu", "B", 9)
        headers = ["Nom du groupe", "N° étudiants", "Moy. note", "Moy. temps min", "Caractéristique"]
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], row_height, header, 1, 0, "C")
        pdf.ln(row_height)

        # Contenu du tableau
        pdf.set_font("DejaVu", "", 8)
        for _, row in profil_df.iterrows():
            # Sauvegarder la position de départ
            x_start = pdf.get_x()
            y_start = pdf.get_y()

            # Cellule multi-ligne temporaire pour estimer la hauteur nécessaire
            tmp_pdf = FPDF()
            tmp_pdf.add_page()
            tmp_pdf.add_font('DejaVu', '', 'fonts/DejaVuSans.ttf', uni=True)
            tmp_pdf.set_font("DejaVu", "", 8)
            tmp_pdf.set_xy(0, 0)
            tmp_pdf.multi_cell(col_widths[4], row_height, str(row["Caractéristique principale"]))
            cell_height = tmp_pdf.get_y()

            max_height = max(row_height, cell_height)

            # Repositionnement pour dessiner les autres cellules à la même hauteur
            pdf.set_xy(x_start, y_start)
            pdf.cell(col_widths[0], max_height, str(row["Nom du groupe"]), 1)
            pdf.cell(col_widths[1], max_height, str(row["Nombre d'étudiants"]), 1, 0, "C")
            pdf.cell(col_widths[2], max_height, str(row["Note moyenne"]), 1, 0, "C")
            pdf.cell(col_widths[3], max_height, str(row["Temps moyen (min)"]), 1, 0, "C")

            # Dernière cellule multi-ligne
            x = pdf.get_x()
            y = pdf.get_y()
            pdf.multi_cell(col_widths[4], row_height, str(row["Caractéristique principale"]), 1)
            
            # Replacer le curseur à gauche pour la prochaine ligne
            pdf.set_xy(x_start, y_start + max_height)


    # Ajouter les Top 5 Étudiants par Filière
    if top_students_dict is not None:
        pdf.add_page()
        pdf.set_font("DejaVu", "B", 14)
        pdf.cell(200, 10, "Top 5 Étudiants par Filière", ln=True)
        pdf.ln(5)

        for filiere, students_df in top_students_dict.items():
            pdf.set_font("DejaVu", "B", 12)
            pdf.cell(200, 10, f"Filière : {filiere}", ln=True)
            pdf.ln(2)

            # Colonnes à afficher
            columns = ["Nom Complet", "Note/20,00", "Temps utilisé (min)"]
            if "Émotion" in students_df.columns:
                columns.append("Émotion")

            # Largeurs approximatives pour chaque colonne
            col_widths = [60, 30, 40, 50][:len(columns)]
            row_height = 7

            pdf.set_font("DejaVu", "B", 9)
            for i, col in enumerate(columns):
                pdf.cell(col_widths[i], row_height, col, 1, 0, "C")
            pdf.ln(row_height)

            pdf.set_font("DejaVu", "", 8)
            for _, row in students_df.iterrows():
                for i, col in enumerate(columns):
                    text = str(row[col]) if col in row else ""
                    pdf.cell(col_widths[i], row_height, text[:40], 1)  # Troncature éventuelle
                pdf.ln(row_height)

            pdf.ln(4)


    pdf_output_path = os.path.join(temp_dir, f"{uuid.uuid4()}.pdf")
    pdf.output(pdf_output_path)

    # Nettoyer les fichiers temporaires
    os.remove(file1_path)
    os.remove(file2_path)
    if fig3 is not None:
        os.remove(file3_path)

    return pdf_output_path