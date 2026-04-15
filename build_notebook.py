import json

notebook = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Analyse de Données Industrielles\n",
    "\n",
    "Ce projet simule l'analyse de données de production d'une usine. L'objectif est de nettoyer les données, de les interroger en SQL pour en tirer des insights, de créer des visualisations pour comprendre les performances de l'entreprise, et enfin d'exporter un flux propre pour la construction d'un Dashboard Power BI.\n",
    "\n",
    "## 1. Importation des librairies et chargement des données"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\n",
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "import seaborn as sns\n",
    "import sqlite3\n",
    "import os\n",
    "\n",
    "# Configuration visuelle de base\n",
    "sns.set_theme(style=\"whitegrid\")\n",
    "plt.rcParams['figure.figsize'] = (10, 6)\n",
    "\n",
    "# Chargement des données brutes\n",
    "df_raw = pd.read_csv('industrial_data_raw.csv')\n",
    "\n",
    "# Aperçu des données\n",
    "display(df_raw.head())\n",
    "display(df_raw.info())"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 2. Nettoyage des données (Data Cleaning)\n",
    "\n",
    "Dans cette section, nous identifions et traitons les valeurs manquantes, les doublons et les valeurs aberrantes (outliers)."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "df_clean = df_raw.copy()\n",
    "\n",
    "# 1. Conversion des dates\n",
    "df_clean['Date'] = pd.to_datetime(df_clean['Date'])\n",
    "\n",
    "# 2. Suppression des doublons\n",
    "print(f\"Doublons avant nettoyage : {df_clean.duplicated().sum()}\")\n",
    "df_clean = df_clean.drop_duplicates()\n",
    "\n",
    "# 3. Traitement des valeurs manquantes\n",
    "# Pour les capteurs (Température et Pression), on peut imputer par la médiane de la machine sur la ligne de production.\n",
    "df_clean['Temperature_C'] = df_clean['Temperature_C'].fillna(df_clean.groupby('Machine_ID')['Temperature_C'].transform('median'))\n",
    "df_clean['Pression_bar'] = df_clean['Pression_bar'].fillna(df_clean.groupby('Machine_ID')['Pression_bar'].transform('median'))\n",
    "\n",
    "# Pour la quantité défectueuse, si elle manque on suppose 0 (optimiste) ou on drope la ligne.\n",
    "df_clean['Quantite_Defectueuse'] = df_clean['Quantite_Defectueuse'].fillna(0)\n",
    "\n",
    "# 4. Traitement des valeurs aberrantes\n",
    "# Température ne peut pas être négative ou extrêmement élevée (>150)\n",
    "valeurs_aberrantes_temp = df_clean[(df_clean['Temperature_C'] < 0) | (df_clean['Temperature_C'] > 150)]\n",
    "print(f\"Nb valeurs aberrantes Température : {len(valeurs_aberrantes_temp)}\")\n",
    "# Remplacement par NaN puis interpolation ou médiane : on remplace par la médiane de la machine\n",
    "median_temp = df_clean.groupby('Machine_ID')['Temperature_C'].transform('median')\n",
    "df_clean['Temperature_C'] = np.where((df_clean['Temperature_C'] < 0) | (df_clean['Temperature_C'] > 150), median_temp, df_clean['Temperature_C'])\n",
    "\n",
    "print(f\"\\nTaille du dataset propre : {len(df_clean)} lignes\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 3. Analyse avec SQL\n",
    "\n",
    "L'utilisation de SQL est primordiale pour un Data Analyst. Nous allons insérer le dataframe dans une base de données locale `sqlite3` en mémoire pour l'interroger."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Connexion à une base de données en mémoire\n",
    "conn = sqlite3.connect(':memory:')\n",
    "\n",
    "# Insertion du dataframe dans la base\n",
    "df_clean.to_sql('production', conn, index=False, if_exists='replace')\n",
    "\n",
    "# Ajout d'une colonne Taux_Defaut dans la requête SQL\n",
    "query = \"\"\"\n",
    "SELECT \n",
    "    Machine_ID,\n",
    "    Ligne_Production,\n",
    "    SUM(Heures_Arret) AS Total_Heures_Arret,\n",
    "    SUM(Quantite_Defectueuse) * 100.0 / SUM(Quantite_Produite) AS Taux_Defaut_Moyen,\n",
    "    AVG(Temperature_C) AS Temp_Moyenne\n",
    "FROM \n",
    "    production\n",
    "GROUP BY \n",
    "    Machine_ID, Ligne_Production\n",
    "ORDER BY \n",
    "    Total_Heures_Arret DESC;\n",
    "\"\"\"\n",
    "\n",
    "df_sql_result = pd.read_sql_query(query, conn)\n",
    "display(df_sql_result)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "**Observation SQL :** \n",
    "Nous avons identifié les machines connaissant le plus de temps d'arrêt et analysé leur taux de défaut. Ces informations pourront être visualisées dans Power BI."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 4. Visualisation des données (Python)\n",
    "\n",
    "Visualisons la distribution des temps d'arrêt par machine et la corrélation éventuelle entre la température et les défauts."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# 1. Temps d'arrêt par machine\n",
    "plt.figure(figsize=(10,6))\n",
    "sns.barplot(data=df_sql_result, x='Machine_ID', y='Total_Heures_Arret', palette='viridis')\n",
    "plt.title(\"Volume total des temps d'arrêt par Machine\")\n",
    "plt.ylabel(\"Heures d'arrêt\")\n",
    "plt.xlabel(\"Machine\")\n",
    "plt.show()\n",
    "\n",
    "# 2. Calcul du taux de défaut pour la corrélation\n",
    "df_clean['Taux_Defaut'] = (df_clean['Quantite_Defectueuse'] / df_clean['Quantite_Produite']) * 100\n",
    "df_clean['Taux_Defaut'] = df_clean['Taux_Defaut'].fillna(0)\n",
    "\n",
    "# 3. Corrélation Température vs Taux de défaut\n",
    "plt.figure(figsize=(10,6))\n",
    "sns.scatterplot(data=df_clean, x='Temperature_C', y='Taux_Defaut', hue='Ligne_Production', alpha=0.5)\n",
    "plt.title(\"Relation entre Température et Taux de Défaut\")\n",
    "plt.xlabel(\"Température (°C)\")\n",
    "plt.ylabel(\"Taux de Défaut (%)\")\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 5. Export des données pour Dashboard Power BI\n",
    "\n",
    "Afin de fournir la restitution visuelle demandée pour la Direction, nous allons exporter ce jeu de données propre sous format CSV. Ce fichier sera notre source d'importation dans Power BI."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Préparation des colonnes finales de manière optimisée\n",
    "cols_to_export = [\n",
    "    'Date', 'Machine_ID', 'Ligne_Production', \n",
    "    'Temperature_C', 'Pression_bar', \n",
    "    'Quantite_Produite', 'Quantite_Defectueuse', 'Taux_Defaut',\n",
    "    'Heures_Fonctionnement', 'Heures_Arret'\n",
    "]\n",
    "\n",
    "df_export = df_clean[cols_to_export]\n",
    "\n",
    "# Export\n",
    "export_path = 'industrial_data_cleaned.csv'\n",
    "df_export.to_csv(export_path, index=False, decimal='.', sep=',')\n",
    "\n",
    "print(f\"Les données propres ont été exportées vers : {export_path}\")"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "name": "python",
   "version": "3.10"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}

with open("analyse_industrielle.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=1)
    print("Notebook analyse_industrielle.ipynb généré avec succès.")
