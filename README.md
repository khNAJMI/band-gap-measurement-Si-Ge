# 🔋 Measurement of the Energy Band Gap of Silicon and Germanium

<p align="center">
  <em>Experimental determination of the band gap of Si and Ge by two independent methods:
  temperature-dependent electrical characterization and optical spectroscopy.</em>
</p>

## 📖 Overview

This project measures the energy band gap **Eg** of two fundamental semiconductors using
**two complementary experimental approaches**:

1. **Electrical method** — temperature-dependent I–V characterization of PN diodes (Si and Ge).
   After difficulties with the classical Shockley logarithmic fit, a **constant-current method**
   was adopted: the forward voltage Vf is extracted at a fixed current of 50 µA for each
   temperature, and linear extrapolation of Vf(T) to T = 0 K yields Eg.
2. **Optical method** (Si only) — **Raman spectroscopy** (520 cm⁻¹ peak confirming crystalline
   silicon) and **photoluminescence spectroscopy** (emission peak near 1070 nm) for an
   independent optical estimate of Eg.

The complete Python data-processing pipeline and the full laboratory report are included.

## 📊 Results

| Material | Method | Eg (experimental) | Reference | Relative error |
|---|---|---|---|---|
| Silicon | Electrical (I–V vs T) | **1.283 eV** | 1.17 eV (0 K) | 9.6% |
| Germanium | Electrical (I–V vs T) | **0.709 eV** | 0.74 eV (0 K) | 4.1% |
| Silicon | Optical (PL) | **≈ 1.16 eV** | 1.12 eV (300 K) | 3.6% |

## 🖥️ Data Analysis Pipeline

The Python scripts process the raw I–V curves (one Excel sheet per temperature):

1. **Offset correction** — the current offset is estimated near V ≈ 0 and subtracted from
   all measurements.
2. **Forward-bias extraction** — only the forward branch (corrected current > 0) is kept.
3. **Constant-current interpolation** — the forward voltage Vf at exactly 50 µA is found by
   interpolation on each temperature sheet.
4. **Linear regression** — Vf(T) = a·T + b is fitted (R² reported).
5. **Extrapolation to T = 0 K** — the intercept b gives the band gap in eV, plotted with the
   experimental data and the extrapolation line.

## 📁 Repository Structure

## 🚀 Usage

```bash
pip install numpy scipy pandas matplotlib openpyxl
python silicium-code.py    # or Germanium-code.py
```

Each script opens a file dialog to select the corresponding Excel file, then prints the
extracted (T, Vf) table, the regression parameters, the band gap and the relative error,
and displays the final Vf(T) plot with the extrapolation to 0 K.

## 📚 Report Contents

Shockley diode equation and saturation-current temperature dependence · constant-current
method theory · experimental setup and measurement chain · uncertainty analysis (regression,
voltage, thermocouple — full propagation) · Raman material identification · photoluminescence
band gap measurement · synthesis and discussion · industrial relevance (photovoltaics,
microelectronics, photodetection, radiation detection)

## 👥 Authors

- **Khawla Najmi**
- **Ibtissam Ait Haddou**

*Supervised by Prof. Vivek Chaudhary and Prof. Jean Decker — School of Applied and
Engineering Physics, UM6P, June 2026*

## 📄 License

MIT License — see [LICENSE](LICENSE).
