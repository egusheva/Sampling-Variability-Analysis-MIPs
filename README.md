# Subsampling Analysis for Sampling Variability in Model Intercomparison Exercises


**Authors:** Ema Gusheva, Alexis Derumigny (subsampling methodology)

---

## Overview

This repository contains the R code used to assess how sensitive model intercomparison study outputs are to the composition of the model ensemble. The core idea is: *if different models had participated in the study, how different would the outputs have been?*

To answer this, we apply a **subsampling approach** to estimate the variance of key summary statistics (median, minimum, maximum, range, mean, and interquartile range) computed from model projection ensembles. A small estimated variance implies that the study outputs are robust to ensemble composition; a large variance implies they are not.

We use subsampling rather than jackknife resampling (which is statistically inconsistent for this task) or bootstrapping (which is not valid for statistics such as the minimum and maximum). The asymptotic validity of the variance estimation procedure is proved in Note S1 of the associated paper.

The analysis focuses on projections for the year **2050** across six model intercomparison databases (CDLINKS, ENGAGE, and ECEMF, each in baseline and policy scenarios), broken down by energy carrier.

---

## Repository structure

```
.
├── functions.R                            # Core subsampling function
├── Estimators-and-Variances.Rmd           # Main R Markdown report (loops over all datasets and carriers)
├── Estimators-and-Variances-section.Rmd   # Template for a single dataset–carrier section (called by the main report)
├── data/                                  # Input data (not included — see Data section below)
│   ├── CDLINKS baseline aggregated.xlsx
│   ├── CDLINKS policy aggregated.xlsx
│   ├── ENGAGE baseline aggregated.xlsx
│   ├── ENGAGE policy aggregated.xlsx
│   ├── ECEMF baseline aggregated.xlsx
│   └── ECEMF policy aggregated.xlsx
└── outputs/                               # Generated automatically on knit
    └── all_results_combined.xlsx          # Combined results table across all datasets and carriers
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

### What the output shows

For each dataset–carrier combination, the analysis produces:

- A histogram of the 2050 projections across the ensemble
- A plot of the estimated standard error as a function of subsample size *b*, with the chosen threshold *b = ⌈n^(2/3)⌉* marked
- A summary table of estimator values and their associated standard errors and variances at the chosen subsample size

All results are also exported to `outputs/all_results_combined.xlsx`.

---

## Requirements

R (≥ 4.1) with the following packages:

```r
install.packages(c("tidyverse", "rmarkdown", "bookdown", "knitr",
                   "readxl", "writexl", "gt", "xfun"))
```

---

## Usage

1. Place the six input `.xlsx` files in a `data/` subdirectory (see structure above).
2. Open `Estimators-and-Variances.Rmd` in RStudio (or knit from the command line).
3. Knit the document:

```r
rmarkdown::render("Estimators-and-Variances.Rmd")
```

The output is a dated `.docx` report (e.g. `Estimators-and-Variances-2025-06-12.docx`) and an Excel summary file at `outputs/all_results_combined.xlsx`.

`Estimators-and-Variances-section.Rmd` is a **template** used internally by the main report via `knitr::knit_expand()`. It does not need to be knitted directly.

---

## Data

The input data files are not included in this repository. They contain aggregated model projections from three model intercomparison studies:

- **CDLINKS** — [https://www.cd-links.org](https://www.cd-links.org)
- **ENGAGE** — [https://www.engage-climate.org](https://www.engage-climate.org)
- **ECEMF** — [https://www.ecemf.eu](https://www.ecemf.eu)

Each file contains projections by energy carrier and model run, with a column for the year 2050.

