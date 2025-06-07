import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import plotly.express as px
from sklearn.preprocessing import StandardScaler
import joblib
import os
import pdf_generator as pg

# Configuration de la page Streamlit
st.set_page_config(page_title="Émotionnella", layout="wide")
st.title("Émotionnella - Analyse des Émotions Étudiantes")

# Initialisation des variables de session si nécessaire
if 'admin_auth' not in st.session_state:
    st.session_state.admin_auth = False
if 'show_password' not in st.session_state:
    st.session_state.show_password = False

# --- Chargement du modèle de clustering ---
@st.cache_resource
def load_model():
    return joblib.load("clustering_model.pkl")

model_dict = load_model()
model = model_dict["kmeans"]
scaler = model_dict.get("scaler", StandardScaler())

# --- Authentification Admin ---
def gestion_auth_admin():
    if 'admin_auth' not in st.session_state:
        st.session_state.admin_auth = False
    if 'show_password' not in st.session_state:
        st.session_state.show_password = False
    
    # Affichage du bouton de cadenas
    col1, col2 = st.sidebar.columns([1, 5])
    with col1:
        if st.session_state.admin_auth:
            # Afficher un cadenas ouvert si authentifié
            if st.button("🔓", help="Cliquez pour déconnecter"):
                st.session_state.admin_auth = False
                st.session_state.show_password = False
                st.rerun()
        else:
            # Afficher un cadenas fermé si non authentifié
            if st.button("🔒", help="Cliquez pour vous connecter"):
                st.session_state.show_password = not st.session_state.show_password
                st.rerun()
    
    with col2:
        if st.session_state.admin_auth:
            st.success("Mode administrateur activé")
        elif st.session_state.show_password:
            st.write("Entrez le mot de passe:")

    # Afficher le champ de mot de passe si nécessaire
    if st.session_state.show_password and not st.session_state.admin_auth:
        mdp = st.sidebar.text_input("", type="password")
        if mdp == "emotionnella123":
            st.session_state.admin_auth = True
            st.session_state.show_password = False
            st.sidebar.success("Authentification réussie!")
            st.rerun()
        elif mdp != "":
            st.sidebar.error("Mot de passe incorrect")
    
    return st.session_state.admin_auth

# Appel de la fonction d'authentification
admin_mode = gestion_auth_admin()

# --- Paramètres de données ---
st.sidebar.header("Paramètres de données")
source = st.sidebar.radio("Source des données", ["Fichiers internes", "Téléverser un fichier"])

# --- Chargement et nettoyage des données ---
@st.cache_data
def load_default_data():
    return pd.read_excel("donnees_etudiants.xlsx")

def convert_time(time_str):
    if pd.isna(time_str) or time_str == "-":
        return np.nan
    
    # Convertir en string si ce n'est pas déjà le cas
    if not isinstance(time_str, str):
        return float(time_str)
    
    # Cas 1: Format "X heures Y min"
    if 'heures' in time_str:
        parts = time_str.split('heures')
        heures = float(parts[0].strip())
        reste = parts[1].strip()
        
        if 'min' in reste:
            mins = float(reste.split('min')[0].strip())
        else:
            mins = 0
        return heures * 60 + mins
    
    # Cas 2: Format "X min Y s" 
    elif 'min' in time_str:
        parts = time_str.split('min')
        mins = float(parts[0].strip())
        secs = float(parts[1].replace('s', '').strip()) if 's' in parts[1] else 0
        return mins + secs / 60
    
    # Cas 3: Format "X s" 
    elif 's' in time_str:
        return float(time_str.replace('s', '').strip()) / 60
    
    # Si aucun format reconnu
    else:
        try:
            return float(time_str) 
        except:
            return np.nan

@st.cache_data
def nettoyer_donnees(df):    
    # 1. Création du Nom Complet
    if 'Prénom' in df.columns and 'Nom' in df.columns and 'Nom Complet' not in df.columns:
        df['Nom Complet'] = df['Prénom'] + ' ' + df['Nom']
    
    # 2. Identification des colonnes de questions avec format standard
    question_cols = [col for col in df.columns if col.startswith('Q.') and '/1,00' in col]
    
    if not question_cols:
        question_cols = [col for col in df.columns if col.startswith('Q.')]
    
    # 3. Traitement des colonnes numériques (questions et note finale)
    important_numcols = ['Note/20,00']
    if question_cols:
        for col in question_cols + important_numcols:
            if col in df.columns:
                # Remplacer tirets, virgules et convertir en float
                df[col] = df[col].replace("-", np.nan)
                if df[col].dtype == object:
                    df[col] = df[col].str.replace(',', '.', regex=False).astype(float)
        
        # Supprimer les lignes où la note finale est NaN
        if 'Note/20,00' in df.columns:
            df = df.dropna(subset=['Note/20,00'])
        
        # Remplire les NaN des questions par 0
        df[question_cols] = df[question_cols].fillna(0)
    
    # 4. Traitement du temps
    if 'Temps utilisé' in df.columns and 'Temps utilisé (min)' not in df.columns:
        df['Temps utilisé (min)'] = df['Temps utilisé'].apply(convert_time)
        df = df.drop('Temps utilisé', axis=1)
    
    # 5. Limitation du temps autorisé à 35 minutes
    if 'Temps utilisé (min)' in df.columns:
        df = df[df['Temps utilisé (min)'] < 20]
    
    # 6. Normalisation des noms de colonnes pour les questions
    rename_dict = {}
    for col in question_cols:
        if '/1,00' in col:
            new_name = col.split('/')[0].strip()
            rename_dict[col] = new_name
    
    if rename_dict:
        df = df.rename(columns=rename_dict)
    
    # 7. Réorganisation et sélection des colonnes importantes
    important_cols = ['Nom Complet', 'Filière', 'Temps utilisé (min)', 'Note/20,00']
    # Mise à jour des colonnes de questions après renommage
    question_cols = [col for col in df.columns if col.startswith('Q.')]
    
    # Conserver uniquement les colonnes importantes qui existent
    cols_to_keep = [col for col in important_cols if col in df.columns] + question_cols
    
    if cols_to_keep:
        df = df[cols_to_keep]

    return df.dropna().drop_duplicates()

if source == "Téléverser un fichier":
    uploaded_files = st.file_uploader("Choisissez un ou plusieurs fichiers .xlsx ou .csv", 
                                     type=["xlsx", "csv"], accept_multiple_files=True)
    
    if uploaded_files:
        # Traitement s'il y a plusieurs fichiers
        if len(uploaded_files) > 1:
            st.info(f"{len(uploaded_files)} fichiers téléversés. Fusion en cours...")
            
            df_list = []
            for file in uploaded_files:
                try:
                    # Déterminer le format du fichier
                    if file.name.endswith(".csv"):
                        temp_df = pd.read_csv(file)
                    else:
                        temp_df = pd.read_excel(file)
                    
                    # Supprimer la dernière ligne si c'est une moyenne
                    if "Moyenne" in str(temp_df.iloc[-1].values):
                        temp_df = temp_df.iloc[:-1]
                        
                    # Extraire la filière du nom de fichier
                    import re
                    filiere_match = re.search(r'MTU\s+(\w+)', file.name)
                    if filiere_match:
                        filiere = filiere_match.group(1)
                    else:
                        # Fallback si le pattern ne correspond pas
                        if "-" in file.name:
                            filiere = file.name.split("-")[0].strip()
                        else:
                            filiere = file.name.split(".")[0].strip()
                    
                    # Créer la colonne filière 
                    if "Filière" not in temp_df.columns:
                        temp_df["Filière"] = filiere
                    
                    df_list.append(temp_df)
                    
                except Exception as e:
                    st.error(f"Erreur lors du traitement du fichier {file.name}: {str(e)}")
            
            # Fusionner tous les fichiers
            if df_list:
                df = pd.concat(df_list, ignore_index=True)
                # Nettoyer les données
                df = nettoyer_donnees(df)
            else:
                st.error("Aucun fichier n'a pu être traité correctement.")
                st.stop()
            
        else: 
            file = uploaded_files[0]
            try:
                if file.name.endswith(".csv"):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)
                
                # Supprimer la dernière ligne si c'est une moyenne
                if "Moyenne" in str(df.iloc[-1].values):
                    df = df.iloc[:-1]
                    
                # Extraire la filière du nom de fichier
                import re
                filiere_match = re.search(r'MTU\s+(\w+)', file.name)
                if filiere_match:
                    filiere = filiere_match.group(1)
                else:
                    # Fallback si le pattern ne correspond pas
                    if "-" in file.name:
                        filiere = file.name.split("-")[0].strip()
                    else:
                        filiere = file.name.split(".")[0].strip()
                
                # Créer la colonne filière 
                if "Filière" not in df.columns:
                    df["Filière"] = filiere
                
                # Nettoyer les données
                df = nettoyer_donnees(df)
                
            except Exception as e:
                st.error(f"Erreur lors du traitement du fichier {file.name}: {str(e)}")
                st.stop()
    else:
        st.warning("Veuillez téléverser un fichier pour continuer.")
        st.stop()
else:
    df = load_default_data()

# --- Anonymisation des noms ---
def anonymiser_nom(nom_complet):
    parts = nom_complet.split()
    if len(parts) >= 2:
        return f"{parts[0]} {parts[1][0]}."
    return nom_complet

if not admin_mode and "Nom Complet" in df.columns:
    df["Nom Complet"] = df["Nom Complet"].apply(anonymiser_nom)

# --- Filtrage par filière ---
if "Filière" in df.columns:
    filieres = df["Filière"].unique().tolist()
    filieres_selectionnees = st.multiselect("Choisissez les filières à analyser", filieres, default=filieres)
    df = df[df["Filière"].isin(filieres_selectionnees)]

# --- Aperçu ---
st.subheader("Aperçu des données")
st.dataframe(df)

# --- Graphiques ---
question_cols = [col for col in df.columns if col.startswith("Q.")]

# Boxplot de la note par filière
st.subheader("Distribution des Notes par Filière")
fig1 = px.box(df, x="Filière", y="Note/20,00", color="Filière")
st.plotly_chart(fig1, use_container_width=True, key="box_plot") 

# Bar chart du taux de réussite par question
st.subheader("Taux de Réussite par Question")
taux_reussite = df[question_cols].mean() * 100
taux_df = taux_reussite.reset_index()
taux_df.columns = ["Question", "Taux de Réussite (%)"]

fig2 = px.bar(
    taux_df,
    x="Question",
    y="Taux de Réussite (%)",
    color="Taux de Réussite (%)",
    color_continuous_scale="Blues"
)
st.plotly_chart(fig2, use_container_width=True, key="bar_plot")

# --- Top 5 Étudiants par Filière ---
st.subheader("Top 5 des Étudiants par Filière")

# Fonction pour obtenir les 5 meilleurs étudiants par filière
def get_top_students(dataframe, n=5):
    # Grouper par filière et trier par note dans chaque groupe
    top_students_dict = {}
    
    for filiere in dataframe["Filière"].unique():
        # Filtrer par filière
        filiere_df = dataframe[dataframe["Filière"] == filiere]
        # Trier par note décroissante
        filiere_df = filiere_df.sort_values(by="Note/20,00", ascending=False)
        # Prendre les n premiers
        top_n = filiere_df.head(n)
        top_students_dict[filiere] = top_n
    
    return top_students_dict

# Obtenir les top 5 étudiants par filière
top_students_dict = get_top_students(df, n=5)

# Afficher les top 5 pour chaque filière dans des onglets
tabs = st.tabs(list(top_students_dict.keys()))

for i, (filiere, students_df) in enumerate(top_students_dict.items()):
    with tabs[i]:
        # Ajouter un emoji médaille pour les 3 premiers
        medals = ["", "", "", "", ""]
        students_display = students_df.copy()
        students_display.reset_index(drop=True, inplace=True)
        students_display.index = students_display.index + 1  # Commencer à 1 au lieu de 0
        
        # Ajouter une colonne pour les médailles
        if len(students_display) > 0:
            students_display["Rang"] = [f"{medals[i-1]} {i}" if i <= len(medals) else f"{i}" for i in range(1, len(students_display) + 1)]
            
            # Réorganiser les colonnes
            cols = ["Rang", "Nom Complet", "Note/20,00", "Temps utilisé (min)"]
            if "Émotion" in students_display.columns:
                cols.append("Émotion")
            
            # Sélectionner uniquement les colonnes qui existent
            existing_cols = [col for col in cols if col in students_display.columns]
            
            # Afficher le tableau
            st.dataframe(students_display[existing_cols], hide_index=True)
            
            # Afficher des statistiques supplémentaires
            st.markdown(f"**Note moyenne des 5 meilleurs**: {students_display['Note/20,00'].mean():.2f}/20")
            if "Temps utilisé (min)" in students_display.columns:
                st.markdown(f"**Temps moyen des 5 meilleurs**: {students_display['Temps utilisé (min)'].mean():.2f} minutes")
        else:
            st.info(f"Aucun étudiant trouvé pour la filière {filiere}")

# --- Clustering ---
st.subheader("Clustering des Étudiants avec KMeans (4 groupes)")
if "Temps utilisé (min)" in df.columns and "Note/20,00" in df.columns:
    X = df[["Temps utilisé (min)", "Note/20,00"]].values
    X_scaled = scaler.transform(X)
    labels = model.predict(X_scaled)
    df["Cluster"] = labels + 1

    # Mappage des clusters aux émotions
    legendes_emotions = {
        1: "Confiant(e) mais prenant son temps", 
        2: "Stressé(e)",  
        3: "Frustré(e) ou abandonné(e)",  
        4: "Confiant(e) rapide"
    }
    
    df["Émotion"] = df["Cluster"].map(legendes_emotions)
    
    # Mappage des couleurs selon l'émotion du cluster
    cluster_colors = {
        "Confiant(e) mais prenant son temps": "#FFABAB",  # Rose clair
        "Stressé(e)": "#83C9FF",  # Bleu clair
        "Frustré(e) ou abandonné(e)": "#0068C9",  # Bleu foncé
        "Confiant(e) rapide": "#FF2B2B"  # Rouge vif
    }

    # Création du graphique
    fig3 = px.scatter(df, x="Temps utilisé (min)", y="Note/20,00", color="Émotion", symbol="Filière",
                      title="Clustering des Étudiants selon l'Émotion", hover_data=["Nom Complet"],
                      color_discrete_map=cluster_colors)

    st.plotly_chart(fig3)

    # Créer un tableau de résumé pour les clusters
    df = df.reset_index(drop=True)
    profil_clusters = []

    for cluster in sorted(df['Cluster'].unique()):
        cluster_data = df[df['Cluster'] == cluster]
        nb_etudiants = len(cluster_data)
        note_moy = cluster_data['Note/20,00'].mean()
        temps_moy = cluster_data['Temps utilisé (min)'].mean()

        if note_moy > 15:
            caractere = "✓ Hautes notes avec temps modéré"
        elif note_moy < 5:
            caractere = "⨻ Basses notes avec temps court"
        else:
            caractere = "– Notes moyennes avec temps variable"

        profil_clusters.append({
            "Nom du groupe": f"{legendes_emotions[cluster]}",
            "Nombre d'étudiants": nb_etudiants,
            "Note moyenne": round(note_moy, 2),
            "Temps moyen (min)": round(temps_moy, 2),
            "Caractéristique principale": caractere
        })

    # Convertir en DataFrame
    profil_df = pd.DataFrame(profil_clusters)

    # Afficher dans Streamlit
    st.subheader("Profil des Clusters")
    st.table(profil_df)

# --- Générer le PDF ---
st.subheader("Le Rapport PDF")
if st.button("Générer le PDF du Rapport"):
    # Vérifier si fig3 et profil_df existent
    if 'fig3' in locals() and 'profil_df' in locals():
        pdf_path = pg.generer_pdf(df, fig1, fig2, fig3=fig3, profil_df=profil_df, top_students_dict=top_students_dict)
    else:
        pdf_path = pg.generer_pdf(df, fig1, fig2, top_students_dict=top_students_dict)
        
    with open(pdf_path, "rb") as f:
        st.download_button("Télécharger le Rapport PDF", f, file_name="rapport_emotionnella.pdf")
    os.remove(pdf_path)

# --- section pour visualiser un étudiant spécifique ---
st.subheader("Analyse des Émotions d'un Étudiant Spécifique")

# Déterminer s'il y a des étudiants à analyser
if len(df) > 0 and "Nom Complet" in df.columns:
    # Créer un sélecteur pour choisir un étudiant
    etudiants = sorted(df["Nom Complet"].unique().tolist())
    etudiant_selectionne = st.selectbox("Sélectionnez un étudiant", etudiants)
    
    # Récupérer les données de l'étudiant sélectionné
    etudiant_data = df[df["Nom Complet"] == etudiant_selectionne].iloc[0]
    
    # Créer un affichage en colonnes pour les informations clés
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Note", f"{etudiant_data['Note/20,00']:.2f}/20")
    
    with col2:
        if "Temps utilisé (min)" in etudiant_data:
            st.metric("Temps utilisé", f"{etudiant_data['Temps utilisé (min)']:.2f} min")
    
    with col3:
        if "Émotion" in etudiant_data:
            # Utiliser une couleur différente selon l'émotion
            emotion = etudiant_data["Émotion"]
            emoji = ""
            if "Confiant(e) rapide" in emotion:
                emoji = "😊"
            elif "Confiant(e) mais prenant son temps" in emotion:
                emoji = "🙂"
            elif "Stressé(e)" in emotion:
                emoji = "😰"
            elif "Frustré(e)" in emotion:
                emoji = "😣"
            
            st.metric("État émotionnel", f"{emoji} {emotion}")
    
    # Afficher les performances par question
    question_cols = [col for col in df.columns if col.startswith("Q.")]
    
    if question_cols:
        st.subheader(f"Performance de {etudiant_selectionne} par Question")
        
        # Créer un DataFrame pour les performances aux questions
        performance_data = {
            "Question": question_cols,
            "Score": [etudiant_data[q] for q in question_cols]
        }
        perf_df = pd.DataFrame(performance_data)
                
        # Comparer avec la moyenne de la filière
        if "Filière" in etudiant_data:
            filiere = etudiant_data["Filière"]
            filiere_avg = df[df["Filière"] == filiere][question_cols].mean()
                        
            # Créer un DataFrame pour la comparaison
            compare_data = []
            for q in question_cols:
                compare_data.append({
                    "Question": q,
                    "Score Étudiant": etudiant_data[q],
                    "Moyenne Filière": filiere_avg[q]
                })
            
            compare_df = pd.DataFrame(compare_data)
            
            # Créer un graphique à barres pour la comparaison
            fig_compare = px.bar(compare_df, x="Question", y=["Score Étudiant", "Moyenne Filière"],
                               barmode="group", title=f"Comparaison {etudiant_selectionne} vs Moyenne {filiere}",
                               labels={"value": "Score (0 = Faux, 1 = Correct)", "variable": "Type de Score"})
            st.plotly_chart(fig_compare, use_container_width=True)
    
    # Afficher un récapitulatif des performances et des recommandations
    st.subheader("Analyse et Recommandations")
    
    # Déterminer des recommandations basées sur l'émotion
    if "Émotion" in etudiant_data:
        emotion = etudiant_data["Émotion"]
        note = etudiant_data["Note/20,00"]
        
        st.write(f"### Profil de {etudiant_selectionne}")
        
        if "Confiant(e) rapide" in emotion:
            st.success(f"""
            **État émotionnel détecté: Confiant(e) et rapide** 😊
            
            Cet étudiant démontre une excellente maîtrise du sujet et une gestion efficace du temps.
            - Ses performances sont excellentes, avec une note de {note:.2f}/20
            - Son rythme rapide indique une grande confiance dans ses réponses
            
            **Recommandations:**
            - Continuer à maintenir cette efficacité
            - Peut être encouragé à approfondir d'autres sujets avancés
            - Pourrait aider les autres étudiants en difficulté (tutorat)
            """)
            
        elif "Confiant(e) mais prenant son temps" in emotion:
            st.info(f"""
            **État émotionnel détecté: Confiant(e) mais prenant son temps** 🙂
            
            Cet étudiant montre une bonne maîtrise du sujet mais préfère travailler avec prudence.
            - Sa note de {note:.2f}/20 reflète une bonne compréhension
            - Son temps de travail plus long suggère une approche méticuleuse
            
            **Recommandations:**
            - Travailler sur la gestion du temps tout en maintenant la qualité
            - Exercices avec contraintes de temps pour améliorer la rapidité
            - Garder confiance dans ses premières réponses
            """)
            
        elif "Stressé(e)" in emotion:
            st.warning(f"""
            **État émotionnel détecté: Stressé(e)** 😰
            
            Cet étudiant montre des signes de stress pendant l'examen.
            - Sa note de {note:.2f}/20 pourrait être améliorée
            - Son temps de réponse et ses résultats suggèrent une anxiété de performance
            
            **Recommandations:**
            - Techniques de gestion du stress (respiration)
            - Plus d'exercices pratiques dans des conditions d'examen
            - Établir un plan de révision progressif
            - Envisager des séances de tutorat ou des sessions de questions-réponses
            """)
            
        elif "Frustré(e)" in emotion:
            st.error(f"""
            **État émotionnel détecté: Frustré(e) ou ayant abandonné** 😣
            
            Cet étudiant semble avoir rencontré des difficultés importantes pendant l'examen.
            - Sa note de {note:.2f}/20 indique des lacunes à combler
            - Son comportement suggère un possible abandon ou une grande frustration
            
            **Recommandations:**
            - Identifier les concepts fondamentaux à réviser
            - Prévoir des sessions de rattrapage ciblées
            - Envisager un accompagnement personnalisé
            - Travailler sur la confiance et la persévérance face aux difficultés
            """)
    else:
        st.write("Analyse émotionnelle non disponible pour cet étudiant.")
else:
    st.info("Aucune donnée d'étudiant disponible. Veuillez télécharger un fichier ou sélectionner des filières.")