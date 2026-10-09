# Subsampling Analysis for Sampling Variability in Model Intercomparison Exercises


**Authors:** Ema Gusheva, Alexis Derumigny (subsampling methodology)

---

## Overview

This repository contains the code used to assess how sensitive model intercomparison study outputs are to the composition of the model ensemble. The core idea is: *if different models had participated in the study, how different would the outputs have been?*

To answer this, we apply a **subsampling approach** to estimate the variance of key summary statistics (median, minimum, maximum, range, mean, and interquartile range) computed from model projection ensembles. A small estimated variance implies that the study outputs are robust to ensemble composition; a large variance implies they are not.

We use subsampling rather than jackknife resampling (which is statistically inconsistent for this task) or bootstrapping (which is not valid for statistics such as the minimum and maximum). Note S3 of the associated paper proves that the conditions for the asymptotic validity of this variance estimator are satisfied for the statistics used here.

The analysis focuses on projections for the year **2050** across six model intercomparison databases (CDLINKS, ENGAGE, and ECEMF, each in baseline and policy scenarios), broken down by energy carrier.

The repository also contains the simulation studies reported in the Supplementary Information (Notes S4 and S5), and a complementary simulation study based on Beta distributions.

---

## Repository structure

```
.
├── functions.R                            # Core subsampling function (estimate_V_exhaustive)
├── Estimators-and-Variances.Rmd           # Main R Markdown report (loops over all datasets and carriers)
├── Estimators-and-Variances-section.Rmd   # Template for a single dataset–carrier section (called by the main report)
├── data/                                  # Input data
│   ├── CDLINKS baseline aggregated.xlsx
│   ├── CDLINKS policy aggregated.xlsx
│   ├── ENGAGE baseline aggregated.xlsx
│   ├── ENGAGE policy aggregated.xlsx
│   ├── ECEMF baseline aggregated.xlsx
│   └── ECEMF policy aggregated.xlsx
├── outputs/
│   └── all_results_combined.xlsx          # Combined results table across all datasets and carriers (generated on knit)
├── all_results_combined.xlsx              # Copy of the combined results table
├── NoteS1_SE_by_subsample_size.csv        # Note S1: standard errors for every subsample size
├── NoteS4_simulation.py                   # Note S4: effect of model dependence on the standard errors
├── NoteS4_simulation_results.csv          # Note S4: results (Table S5)
├── NoteS5_simulation.py                   # Note S5: accuracy and coverage of the standard errors at n = 6, 9, 12
├── NoteS5_simulation_results.csv          # Note S5: results (Table S6)
├── Simulation_study_Preparation.Rmd       # Beta distributions fitted to the datasets (A. Derumigny)
└── Simulation_study.Rmd                   # Complementary simulation with Beta distributions and dependence (A. Derumigny)
```

---

## Methods

### Subsampling variance estimation

For a sample of size *n* (the model ensemble), we fix a subsample size *b = ⌈n^(2/3)⌉* and enumerate **all possible subsamples of size *b*** drawn without replacement. For each subsample, we recompute the estimator of interest (e.g. the median). The variance of this empirical distribution, rescaled by a factor that depends on the estimator type, gives an estimate of the variance of the estimator for the full ensemble of size *n*.

The scaling ratios applied per estimator are:

| Estimator | Scaling ratio |
|-----------|--------------|
| min, max, range | (b/n)² |
| median, mean, IQR | b/n |

The square root of the rescaled variance gives the **standard error**, which quantifies the typical shift in a summary statistic expected under an independently drawn alternative ensemble.

### What the main report shows

For each dataset–carrier combination, the analysis produces:

- A histogram of the 2050 projections across the ensemble
- A plot of the estimated standard error as a function of subsample size *b*, with the chosen threshold *b = ⌈n^(2/3)⌉* marked
- A summary table of estimator values and their associated standard errors and variances at the chosen subsample size

All results are also exported to `outputs/all_results_combined.xlsx`.

### Supplementary analyses

- **Note S1 – Sensitivity to the subsample size.** `NoteS1_SE_by_subsample_size.csv` contains the standard error for every dataset, variable, statistic and subsample size from *b* = 3 to *n* − 1 (`se`), and its ratio to the value at the subsample size used in the analysis, *b\** = ⌈n^(2/3)⌉ (`se_ratio`).
- **Note S4 – Model dependence.** `NoteS4_simulation.py` draws synthetic ensembles with equal pairwise dependence between models (a Gaussian copula with Spearman's rho of 0, 0.1, 0.2 and 0.3, uniform margins) and applies the same estimator. The `dependence_factor` column in `NoteS4_simulation_results.csv` gives the ratio of the true standard error to the subsampling estimate, relative to the case without dependence (Table S5). For the mean, it matches the closed-form factor √((1 + (n − 1)ρ)/(1 − ρ)) (`formula_mean`).
- **Note S5 – Accuracy at small ensemble sizes.** `NoteS5_simulation.py` draws 5,000 synthetic ensembles of n = 6, 9 and 12 models from a uniform, a truncated normal and a truncated exponential distribution on [0, 1], applies the same estimator, and compares the estimated standard errors with the true ones, computed from 200,000 independent ensembles. `NoteS5_simulation_results.csv` reports the ratio of estimated to true standard error (Table S6) and the coverage of nominal 95% intervals.

The Python scripts use a vectorised implementation of `estimate_V_exhaustive()` from `functions.R`, which gives identical standard errors.

### Complementary simulation with Beta distributions

`Simulation_study_Preparation.Rmd` fits Beta distributions to the 2050 projections of each dataset and carrier, after rescaling them to [0, 1]. `Simulation_study.Rmd` uses Beta distributions with shapes chosen to reflect these fits, ensemble sizes n = 6, 9 and 12, and a Spearman's rho of 0 or 0.2 between models, and compares the average estimated standard error with the true one. Note that this simulation uses *b* = round(n^(2/3)) (3, 4 and 5), whereas the main analysis and Notes S1, S4 and S5
