import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_industrial_data(num_rows=6000):
    print(f"Machine de génération démarrée. Création de {num_rows} lignes...")
    
    np.random.seed(42)
    random.seed(42)
    
    # Paramètres de base
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(days=random.randint(0, 365), hours=random.randint(0, 23), minutes=random.randint(0, 59)) for _ in range(num_rows)]
    dates.sort()
    
    machines = ['M-001', 'M-002', 'M-003', 'M-004', 'M-005']
    lines = ['Ligne_A', 'Ligne_B', 'Ligne_C']
    
    # Génération des colonnes avec du bruit
    data = []
    
    for dt in dates:
        machine_id = random.choice(machines)
        ligne = "Ligne_A" if machine_id in ['M-001', 'M-002'] else ("Ligne_B" if machine_id in ['M-003', 'M-004'] else "Ligne_C")
        
        # Température avec des anomalies ponctuelles
        temp_base = np.random.normal(70, 5) if ligne == "Ligne_A" else np.random.normal(85, 7)
        if random.random() < 0.05: # 5% de chances d'avoir une température aberrante ou négative (erreur capteur)
            temperature = temp_base * random.uniform(1.5, 2.5) if random.random() > 0.5 else -99.9
        else:
            temperature = temp_base
            
        # Pression (idéalement entre 3 et 6 bar)
        pressure = np.random.normal(4.5, 0.8)
        
        # Quantité produite (entre 100 et 1000 par heure)
        qty_produced = int(np.random.normal(500, 150))
        qty_produced = max(0, qty_produced)
        
        # Quantité défectueuse (fortement corrélée à température extrême ou pression hors norme)
        defect_rate = np.random.uniform(0.01, 0.05)
        if temperature > 100 or pressure < 3.0:
            defect_rate += np.random.uniform(0.05, 0.15)
            
        qty_defective = int(qty_produced * defect_rate)
        
        # Heures de fonctionnement et d'arrêt par shift (Shift de 8h)
        total_shift_hours = 8.0
        downtime = np.random.exponential(0.5) if random.random() < 0.2 else 0.0
        uptime = total_shift_hours - downtime
        
        # Création d'anomalies: Valeurs nulles aléatoires
        if random.random() < 0.02:
            pressure = np.nan
        if random.random() < 0.01:
            qty_defective = np.nan
            
        data.append({
            'Date': dt.strftime("%Y-%m-%d %H:%M:%S"),
            'Machine_ID': machine_id,
            'Ligne_Production': ligne,
            'Temperature_C': round(temperature, 2) if not pd.isna(temperature) else np.nan,
            'Pression_bar': round(pressure, 2) if not pd.isna(pressure) else np.nan,
            'Quantite_Produite': qty_produced,
            'Quantite_Defectueuse': qty_defective if not pd.isna(qty_defective) else np.nan,
            'Heures_Fonctionnement': round(uptime, 2),
            'Heures_Arret': round(downtime, 2)
        })

    df = pd.DataFrame(data)
    
    # Ajout d'anomalies de type "doublons"
    duplicates = df.sample(n=int(num_rows*0.01))
    df = pd.concat([df, duplicates], ignore_index=True)
    
    # Export CSV
    output_filename = 'industrial_data_raw.csv'
    df.to_csv(output_filename, index=False)
    print(f"Jeu de données brut généré avec succès : {output_filename} ({len(df)} lignes).")

if __name__ == "__main__":
    generate_industrial_data(5500)
