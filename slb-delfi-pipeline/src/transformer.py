import pandas as pd

def clean_and_process_telemetry(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applique les filtres de nettoyage industriels et calcule le Water Cut.
    """
    # 1. Suppression des bruits de capteurs (valeurs négatives aberrantes)
    # Dans un puits, une moyenne de pression ou un volume de brut ne peuvent pas être négatifs.
    df_cleaned = df[
        (df['AVG_DOWNHOLE_PRESSURE'] >= 0) & 
        (df['BORE_OIL_VOL'] >= 0) & 
        (df['BORE_WAT_VOL'] >= 0)
    ].copy()
    
    # 2. Calcul du KPI pétrolier : Water Cut (%)
    # Formule : Volume d'eau / (Volume de Pétrole + Volume d'eau)
    # On ajoute 1e-5 (epsilon) au dénominateur pour éviter la division par zéro si le puits est fermé.
    total_volume = df_cleaned['BORE_OIL_VOL'] + df_cleaned['BORE_WAT_VOL']
    df_cleaned['WATER_CUT'] = (df_cleaned['BORE_WAT_VOL'] / (total_volume + 1e-5)) * 100
    
    return df_cleaned