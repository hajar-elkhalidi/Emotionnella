# Émotionnella - Analyse des Émotions Étudiantes

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📋 Description du Projet

**Émotionnella** est un outil d'analyse avancé conçu pour comprendre et analyser les émotions des étudiants lors d'examens ou d'évaluations. Le projet utilise des techniques de machine learning (clustering KMeans) pour identifier automatiquement les états émotionnels des étudiants basés sur leurs performances et leur comportement temporel.

### 🎯 Objectifs

- **Identifier les états émotionnels** des étudiants pendant les examens
- **Analyser les performances** individuelles et collectives
- **Générer des recommandations personnalisées** pour chaque profil d'étudiant
- **Fournir des insights pédagogiques** aux enseignants et administrateurs

## 🚀 Fonctionnalités Principales

### 📊 Tableau de Bord Interactif
- Interface web intuitive développée avec Streamlit
- Visualisations interactives des données avec Plotly
- Anonymisation automatique des données étudiantes (mode non-admin)

### 🔐 Système d'Authentification
- Mode administrateur avec authentification par mot de passe
- Affichage anonymisé des noms d'étudiants en mode public
- Interface sécurisée avec icônes de cadenas

### 📈 Analyses Avancées
- **Clustering émotionnel** : Classification automatique en 4 groupes d'émotions
- **Analyse comparative** : Comparaison par filière et par étudiant
- **Top 5 des meilleurs étudiants** par filière
- **Taux de réussite** par question

### 🎭 Détection des États Émotionnels

Le système identifie 4 profils émotionnels principaux :

1. **😊 Confiant(e) rapide** - Excellentes performances avec gestion efficace du temps
2. **🙂 Confiant(e) mais prenant son temps** - Bonnes performances avec approche méticuleuse  
3. **😰 Stressé(e)** - Performances moyennes avec signes d'anxiété
4. **😣 Frustré(e) ou abandonné(e)** - Difficultés importantes, possibles lacunes

### 📄 Génération de Rapports
- Export PDF complet avec tous les graphiques et analyses
- Recommandations personnalisées pour chaque étudiant
- Synthèse des profils de clusters

## 🛠️ Installation et Configuration

### Prérequis
```bash
Python 3.10
pip (gestionnaire de packages Python)
```

### Installation des Dépendances
```bash
pip install -r requirements.txt
```

### Structure du Projet
```
emotionnella/
├── fonts/                    # Le font utilisé dans le rapport
├── app.py                    # Application principale Streamlit
├── pdf_generator.py          # Module de génération PDF
├── clustering_model.pkl      # Modèle KMeans pré-entraîné
├── donnees_etudiants.xlsx   # Fichier de données par défaut
├── README.md                # Ce fichier
└── requirements.txt         # Dépendances Python
```

### Lancement de l'Application
```bash
streamlit run app.py
```

L'application sera accessible à l'adresse : `http://localhost:8501`

## 📊 Utilisation

### 1. Authentification
- Cliquez sur l'icône 🔒 dans la barre latérale
- Entrez le mot de passe : `emotionnella123`
- Mode admin activé : accès aux noms complets des étudiants

### 2. Chargement des Données
**Option 1 : Fichiers internes**
- Utilise le fichier `donnees_etudiants.xlsx` par défaut

**Option 2 : Téléversement**
- Formats supportés : `.xlsx`, `.csv`
- Support multi-fichiers avec fusion automatique
- Extraction automatique des filières depuis les noms de fichiers

### 3. Analyse des Données
- **Filtrage par filière** : Sélection multiple possible
- **Visualisations automatiques** : Boxplots, graphiques en barres, scatter plots
- **Clustering émotionnel** : Classification automatique des étudiants

### 4. Analyse Individuelle
- Sélection d'un étudiant spécifique
- Métriques de performance (note, temps, émotion)
- Comparaison avec la moyenne de la filière
- Recommandations personnalisées

## 🔧 Format des Données d'Entrée

### Structure Attendue
```
Colonnes requises :
- Prénom, Nom (ou Nom Complet)
- Filière 
- Note/20,00
- Temps utilisé
- Q.1, Q.2, Q.3, ... (questions avec scores 0/1)
```

### Exemple de Fichier
```csv
Prénom,Nom,Filière,Note/20,00,Temps utilisé,Q.1/1,00,Q.2/1,00,Q.3/1,00
Marie,Dupont,INFO,16.5,15 min 30 s,1,1,0
Pierre,Martin,MATH,12.0,25 min,0,1,1
```

## 🤖 Algorithme de Clustering

### Méthode KMeans
- **Nombre de clusters** : 4 (optimisé pour les états émotionnels)
- **Features utilisées** : Temps utilisé (min) + Note/20
- **Normalisation** : StandardScaler pour équilibrer les échelles

### Mappage Émotionnel
```python
legendes_emotions = {
    1: "Confiant(e) mais prenant son temps", 
    2: "Stressé(e)",  
    3: "Frustré(e) ou abandonné(e)",  
    4: "Confiant(e) rapide"
}
```

## 📈 Métriques et Indicateurs

### Métriques Principales
- **Note moyenne** par filière et par cluster
- **Temps moyen** d'examen par groupe
- **Taux de réussite** par question
- **Distribution des émotions** par filière

### Indicateurs de Performance
- Top 5 des étudiants par filière
- Analyse comparative individuelle vs moyenne
- Profils détaillés des clusters émotionnels

## 🎨 Personnalisation

### Couleurs des Clusters
```python
cluster_colors = {
    "Confiant(e) mais prenant son temps": "#FFABAB",  # Rose clair
    "Stressé(e)": "#83C9FF",                          # Bleu clair
    "Frustré(e) ou abandonné(e)": "#0068C9",          # Bleu foncé
    "Confiant(e) rapide": "#FF2B2B"                   # Rouge vif
}
```

### Paramètres Modifiables
- Seuil de temps maximum : 35 minutes (ligne 157)
- Mot de passe admin : `emotionnella123` (ligne 61)
- Nombre d'étudiants dans le Top : 5 (ligne 321)

## 🔒 Sécurité et Confidentialité

### Protection des Données
- **Anonymisation automatique** en mode non-admin
- **Chiffrement** des noms (Prénom + Initiale du nom)
- **Aucune sauvegarde** des données uploadées

### Conformité RGPD
- Pas de stockage permanent des données personnelles
- Traitement local des données
- Droit à l'oubli respecté (redémarrage = effacement)

## 🐛 Dépannage

### Problèmes Courants

**Erreur de chargement du modèle**
```bash
FileNotFoundError: clustering_model.pkl
```
**Solution** : Vérifiez que le fichier `clustering_model.pkl` est présent dans le dossier

**Erreur de format de temps**
```bash
ValueError: cannot convert float NaN to integer
```
**Solution** : Vérifiez le format de la colonne "Temps utilisé" dans vos données

**Colonnes manquantes**
```bash
KeyError: 'Note/20,00'
```
**Solution** : Assurez-vous que votre fichier contient toutes les colonnes requises

## 📚 Ressources Supplémentaires

### Documentation Technique
- [Documentation Streamlit](https://docs.streamlit.io/)
- [Documentation Plotly](https://plotly.com/python/)
- [Documentation Scikit-learn](https://scikit-learn.org/stable/)

### Références Académiques
- Clustering émotionnel en éducation
- Analyse comportementale des étudiants
- Learning Analytics et Educational Data Mining

## 📜 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🙏 Remerciements et Mentions Importantes

Un grand merci à **Madame** [**Nisrine SAFEH**](https://www.linkedin.com/in/nisrine-safeh-8663b9141/), co-encadrante et responsable ENT à la FSBM, pour sa disponibilité et pour avoir fourni les données du module **MTU S1** des filières **BCG**, **PC**, **IA** et **MTU**.

Merci également à **Madame** [**Sara OUAHABI**](https://www.linkedin.com/in/sara-ouahabi-614b87326/), encadrante du projet, pour son accompagnement tout au long de ce travail.


### 📊 Données utilisées

Les données présentes dans ce dépôt sont **fictives et générées à des fins de démonstration uniquement**.  
Elles ne reflètent en aucun cas les performances réelles d’étudiants ou d’étudiantes.

### 👥 Équipe projet

Ce projet a été réalisé par :

- **Hajar EL KHALIDI**
- [**Hasnae AMEJOUD**](https://www.linkedin.com/in/hasnae-amejoud-10b26634a/)


---

**Émotionnella** - Comprendre les émotions pour mieux enseigner 🎓💡
