import pandas as pd
import numpy as np

# Chargement des données brutes
df_raw = pd.read_csv('industrial_data_raw.csv')

df_clean = df_raw.copy()

# 1. Conversion des dates
df_clean['Date'] = pd.to_datetime(df_clean['Date'])

# 2. Suppression des doublons
df_clean = df_clean.drop_duplicates()

# 3. Traitement des valeurs manquantes
df_clean['Temperature_C'] = df_clean['Temperature_C'].fillna(df_clean.groupby('Machine_ID')['Temperature_C'].transform('median'))
df_clean['Pression_bar'] = df_clean['Pression_bar'].fillna(df_clean.groupby('Machine_ID')['Pression_bar'].transform('median'))
df_clean['Quantite_Defectueuse'] = df_clean['Quantite_Defectueuse'].fillna(0)

# 4. Traitement des valeurs aberrantes
median_temp = df_clean.groupby('Machine_ID')['Temperature_C'].transform('median')
df_clean['Temperature_C'] = np.where((df_clean['Temperature_C'] < 0) | (df_clean['Temperature_C'] > 150), median_temp, df_clean['Temperature_C'])

df_clean['Taux_Defaut'] = (df_clean['Quantite_Defectueuse'] / df_clean['Quantite_Produite']) * 100
df_clean['Taux_Defaut'] = df_clean['Taux_Defaut'].fillna(0)

cols_to_export = [
    'Date', 'Machine_ID', 'Ligne_Production', 
    'Temperature_C', 'Pression_bar', 
    'Quantite_Produite', 'Quantite_Defectueuse', 'Taux_Defaut',
    'Heures_Fonctionnement', 'Heures_Arret'
]

df_export = df_clean[cols_to_export]

# Export
export_path = 'industrial_data_cleaned.csv'
df_export.to_csv(export_path, index=False, decimal='.', sep=',')
print("Data cleaned and exported successfully.")
