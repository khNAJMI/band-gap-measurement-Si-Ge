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
try:
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    file_path = filedialog.askopenfilename(
        title="Sélectionnez votre fichier Excel (silicium all data.xlsx)",
        filetypes=[("Fichiers Excel", "*.xlsx *.xls")]
    )
    root.destroy()
except Exception as e:
    print(f" Erreur d'interface graphique : {e}")
    sys.exit()

if not file_path:
    print(" Erreur : Aucun fichier sélectionné.")
    sys.exit()

print(f"Fichier chargé : {os.path.basename(file_path)}\n")
print("Extraction des données et correction de l'offset en cours...\n")

# ==========================================
# 2. PARAMÈTRES PHYSIQUES
# ==========================================
I_target = 50e-6  # 50 µA

# ==========================================
# 3. LECTURE ET TRAITEMENT PAR TEMPÉRATURE
# ==========================================
all_sheets = pd.read_excel(file_path, sheet_name=None)
results = []

for sheet_name, df in all_sheets.items():
    try:
        T = float(str(sheet_name).strip())
    except ValueError:
        continue
    
    V = pd.to_numeric(df.iloc[:, 0], errors='coerce').dropna().values
    I = pd.to_numeric(df.iloc[:, 1], errors='coerce').dropna().values
    
    if len(V) < 2:
        continue
        
    # Correction robuste de l'offset
    mask_zero = (V >= -0.1) & (V <= 0.1)
    if np.any(mask_zero):
        offset_I = np.mean(I[mask_zero])
    else:
        idx = np.argmin(np.abs(V))
        offset_I = I[idx]
    
    I_corrected = I - offset_I
    mask_fwd = I_corrected > 1e-7
    V_fwd = V[mask_fwd]
    I_fwd = I_corrected[mask_fwd]
    
    if len(V_fwd) < 2:
        continue
        
    sort_idx = np.argsort(I_fwd)
    I_sorted = I_fwd[sort_idx]
    V_sorted = V_fwd[sort_idx]
    
    if I_target < I_sorted[0] or I_target > I_sorted[-1]:
        continue
    
    V_f = np.interp(I_target, I_sorted, V_sorted)
    results.append({'T': T, 'V_f': V_f, 'offset': offset_I})

print(f"Traitement terminé. {len(results)} températures valides extraites.\n")

# ==========================================
# 4. CALCUL DE L'ÉNERGIE DE GAP (Eg) ET AFFICHAGE DÉTAILLÉ
# ==========================================
if len(results) < 3:
    print("❌ Erreur critique : Pas assez de températures valides pour calculer Eg.")
    sys.exit()

# Tri des résultats par température croissante
res_df = pd.DataFrame(results).sort_values('T')
T_vals = res_df['T'].values
Vf_vals = res_df['V_f'].values

# ==========================================
# NOUVEAU : AFFICHAGE DÉTAILLÉ DES VALEURS (T, V_f)
# ==========================================
print("="*65)
print(f"📋 DÉTAIL DES VALEURS EXTRAITES (à I = {I_target*1e6:.0f} µA)")
print("="*65)
print(f"{'Température T (K)':<22} | {'Tension V_f (V)':<15}")
print("-" * 42)
for index, row in res_df.iterrows():
    # Formatage : 2 décimales pour T, 6 décimales pour V_f
    print(f"{row['T']:<22.2f} | {row['V_f']:<15.6f}")
print("="*65 + "\n")

# Régression linéaire : V_f = a * T + b
slope, intercept, r_value, p_value, std_err = linregress(T_vals, Vf_vals)
Eg_eV = intercept

print("="*65)
print(" RÉSULTAT FINAL (Méthode du Courant Constant - SILICIUM)")
print("="*65)
print(f"Courant cible utilisé          : {I_target*1e6:.0f} µA")
print(f"Offset moyen corrigé           : {res_df['offset'].mean()*1e6:.2f} µA")
print(f"Nombre de températures valides : {len(res_df)}")
print(f"Pente dV_f/dT (Coeff temp)     : {slope*1000:.3f} mV/K")
print(f"R² de la régression linéaire   : {r_value**2:.4f}")
print("-" * 65)
print(f" Énergie de Gap Eg (Exp)      : {Eg_eV:.3f} eV")
print(f" Énergie de Gap Eg (Théorique): ~ 1.17 eV (Silicium à 0 K)")
print(f" Erreur relative              : {abs(Eg_eV - 1.17)/1.17 * 100:.1f} %")
print("="*65)

# ==========================================
# 5. TRACÉ DU GRAPHIQUE POUR LE RAPPORT
# ==========================================
plt.figure(figsize=(10, 6))

plt.plot(T_vals, Vf_vals, 'bo', markersize=7, label=f'Données expérimentales (à {I_target*1e6:.0f} µA)')

T_fit = np.array([200, 450])
Vf_fit = slope * T_fit + intercept
plt.plot(T_fit, Vf_fit, 'r--', linewidth=2, 
         label=f'Extrapolation linéaire\nEg ≈ {Eg_eV:.3f} eV\nR² = {r_value**2:.4f}')

plt.plot(0, intercept, 'r*', markersize=15, 
         label=f'Extrapolation à 0 K\n(V_g0 = {intercept:.3f} V)')

plt.title(f'Extraction du Gap Énergétique du Silicium\nMéthode à Courant Constant ({I_target*1e6:.0f} µA)', 
          fontsize=14, fontweight='bold')
plt.xlabel('Température T (K)', fontsize=12)
plt.ylabel('Tension directe V_f (V)', fontsize=12)

plt.xlim(min(T_vals) - 20, max(T_vals) + 20)
plt.ylim(0, max(Vf_vals) * 1.3)

plt.axhline(0, color='black', linewidth=0.8, linestyle=':')
plt.axvline(0, color='black', linewidth=0.8, linestyle=':')
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(fontsize=11, loc='upper right')

plt.tight_layout()
plt.show()