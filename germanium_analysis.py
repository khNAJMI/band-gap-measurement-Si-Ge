import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
import tkinter as tk
from tkinter import filedialog
import os
import sys

# ==========================================
# 1. SÉLECTION DU FICHIER EXCEL
# ==========================================
root = tk.Tk()
root.withdraw()
root.attributes('-topmost', True)

file_path = filedialog.askopenfilename(
    title="Sélectionnez votre fichier Excel (germanium all data.xlsx)",
    filetypes=[("Fichiers Excel", "*.xlsx *.xls")]
)

if not file_path:
    print("❌ Erreur : Aucun fichier sélectionné.")
    sys.exit()

print(f"✅ Fichier chargé : {os.path.basename(file_path)}\n")
print("🔄 Extraction des données et correction de l'offset en cours...\n")

# ==========================================
# 2. PARAMÈTRES PHYSIQUES
# ==========================================
# On fixe le courant à 50 µA. C'est le compromis idéal : 
# assez haut pour être au-dessus du bruit, assez bas pour éviter la résistance série.
I_target = 50e-6  

# ==========================================
# 3. LECTURE ET TRAITEMENT PAR TEMPÉRATURE
# ==========================================
all_sheets = pd.read_excel(file_path, sheet_name=None)
results = []

for sheet_name, df in all_sheets.items():
    # Récupération de la température depuis le nom de l'onglet
    try:
        T = float(str(sheet_name).strip())
    except ValueError:
        continue
    
    # Récupération des colonnes V (0) et I (1)
    V = pd.to_numeric(df.iloc[:, 0], errors='coerce').dropna().values
    I = pd.to_numeric(df.iloc[:, 1], errors='coerce').dropna().values
    
    # --- ÉTAPE CRUCIALE : CORRECTION DE L'OFFSET ---
    # On calcule le courant moyen quand la tension est proche de 0 (entre -0.05V et +0.05V)
    mask_zero = (V >= -0.05) & (V <= 0.05)
    offset_I = np.mean(I[mask_zero])
    
    # On soustrait cet offset de toutes les mesures
    I_corrected = I - offset_I
    
    # On ne garde que la polarisation directe (courant corrigé > 0)
    mask_fwd = I_corrected > 1e-7
    V_fwd = V[mask_fwd]
    I_fwd = I_corrected[mask_fwd]
    
    if len(V_fwd) < 2:
        continue
        
    # Tri par courant croissant (obligatoire pour l'interpolation)
    sort_idx = np.argsort(I_fwd)
    I_sorted = I_fwd[sort_idx]
    V_sorted = V_fwd[sort_idx]
    
    # Vérification que le courant cible est dans la plage mesurée
    if I_target < I_sorted[0] or I_target > I_sorted[-1]:
        continue
    
    # Interpolation pour trouver la tension V_f au courant exact de 50 µA
    V_f = np.interp(I_target, I_sorted, V_sorted)
    
    results.append({'T': T, 'V_f': V_f, 'offset': offset_I})
    
    # Affichage dans la console
    if len(results) % 10 == 0: # Pour ne pas surcharger la console
        print(f"   ... {len(results)} températures traitées.")

print(f"\n✅ Traitement terminé. {len(results)} températures valides extraites.\n")

# ==========================================
# 4. CALCUL DE L'ÉNERGIE DE GAP (Eg)
# ==========================================
if len(results) < 3:
    print("❌ Erreur : Pas assez de températures valides pour calculer Eg.")
    sys.exit()

res_df = pd.DataFrame(results).sort_values('T')
T_vals = res_df['T'].values
Vf_vals = res_df['V_f'].values

# Régression linéaire : V_f = a * T + b
slope, intercept, r_value, p_value, std_err = linregress(T_vals, Vf_vals)

# L'extrapolation à T = 0 K (l'ordonnée à l'origine 'intercept') donne la tension de gap
Eg_eV = intercept

print("="*60)
print(" RÉSULTAT FINAL (Méthode du Courant Constant)")
print("="*60)
print(f"Courant cible utilisé          : {I_target*1e6:.0f} µA")
print(f"Offset moyen corrigé           : {res_df['offset'].mean()*1e6:.1f} µA")
print(f"Nombre de températures valides : {len(res_df)}")
print(f"Pente dV_f/dT (Coeff temp)     : {slope*1000:.3f} mV/K")
print(f"R² de la régression linéaire   : {r_value**2:.4f}")
print("-" * 60)
print(f" Énergie de Gap Eg (Exp)      : {Eg_eV:.3f} eV")
print(f" Énergie de Gap Eg (Théorique): ~ 0.67 eV (Germanium)")
print(f"📉 Erreur relative              : {abs(Eg_eV - 0.67)/0.67 * 100:.1f} %")
print("="*60)

# ==========================================
# 5. TRACÉ DU GRAPHIQUE POUR LE RAPPORT
# ==========================================
plt.figure(figsize=(10, 6))

# Tracé des points expérimentaux
plt.plot(T_vals, Vf_vals, 'bo', markersize=7, label='Données expérimentales (à 50 µA)')

# Tracé de la droite de fit et de l'extrapolation
T_fit = np.array([200, 450]) # Plage étendue pour bien voir l'axe des Y à T=0
Vf_fit = slope * T_fit + intercept
plt.plot(T_fit, Vf_fit, 'r--', linewidth=2, 
         label=f'Extrapolation linéaire\nEg ≈ {Eg_eV:.3f} eV\nR² = {r_value**2:.4f}')

# Point d'extrapolation à T=0 K
plt.plot(0, intercept, 'r*', markersize=15, 
         label=f'Extrapolation à 0 K\n(V_g0 = {intercept:.3f} V)')

# Mise en forme
plt.title(f'Extraction du Gap Énergétique du Germanium\nMéthode à Courant Constant ({I_target*1e6:.0f} µA)', 
          fontsize=14, fontweight='bold')
plt.xlabel('Température T (K)', fontsize=12)
plt.ylabel('Tension directe V_f (V)', fontsize=12)
plt.xlim(250, 430)
plt.ylim(0, max(Vf_vals) * 1.4)
plt.axhline(0, color='black', linewidth=0.8, linestyle=':')
plt.axvline(0, color='black', linewidth=0.8, linestyle=':')
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(fontsize=11, loc='upper right')

plt.tight_layout()
plt.show()
