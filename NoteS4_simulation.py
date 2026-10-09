"""
Note S4 - Sensitivity of subsampling variance estimates to model dependence.

Each synthetic ensemble of n models is drawn with exchangeable dependence: a
Gaussian copula with equal pairwise Spearman's rho between all models (the same
construction as Simulation_study.Rmd, copula::iRho + normalCopula(dispstr="ex")),
here with uniform margins on [0, 1]. With uniform margins, the Pearson
correlation between projections equals Spearman's rho, so for the ensemble mean
the closed-form factor in Note S4 applies directly:

    true SE / subsampling SE = sqrt((1 + (n - 1) * rho) / (1 - rho))

The subsampling estimator is the one used in the analysis (functions.R,
estimate_V_exhaustive: all subsets of size b = ceil(n^(2/3)), no
finite-population correction).

Output: NoteS4_simulation_results.csv (one row per n x rho x statistic)
  true_se            SD of the statistic over R_TRUE dependent ensembles
  mean_est_se        average subsampling SE over R_REP dependent ensembles
  total_factor       true_se / mean_est_se. Combines the effect of dependence
                     with the small-sample underestimation shown in Note S5.
  dependence_factor  total_factor(rho) / total_factor(rho = 0). Isolates the
                     effect of dependence; this is what Table S5 reports.
  formula_mean       closed-form factor above (for the mean only)

Requires numpy, scipy, pandas. Runtime: under a minute.
"""
import itertools
import numpy as np
import pandas as pd
from scipy.special import ndtr          # standard normal CDF

rng = np.random.default_rng(2026)
STATS = ["min", "max", "median", "range", "mean", "iqr"]
RATIO_POW = {"min": 2, "max": 2, "range": 2, "median": 1, "mean": 1, "iqr": 1}


def stats_last_axis(X):
    """Statistics along the last axis; IQR uses linear interpolation (= R type 7)."""
    q1, med, q3 = np.percentile(X, [25, 50, 75], axis=-1)
    mn, mx = X.min(-1), X.max(-1)
    return {"min": mn, "max": mx, "median": med, "range": mx - mn,
            "mean": X.mean(-1), "iqr": q3 - q1}


def subsampling_se(X, b):
    """X: (reps, n). Same estimator as estimate_V_exhaustive() in functions.R."""
    n = X.shape[1]
    idx = np.array(list(itertools.combinations(range(n), b)))
    sub = stats_last_axis(X[:, idx])
    return {s: np.sqrt(sub[s].var(axis=1, ddof=1) * (b / n) ** RATIO_POW[s])
            for s in STATS}


def r_dependent_uniform(reps, n, spearman_rho):
    """reps ensembles of n models; exchangeable Gaussian copula with the given
    Spearman's rho, uniform margins. Gaussian parameter r = 2 sin(pi*rho/6)."""
    r = 2 * np.sin(np.pi * spearman_rho / 6)
    shared = rng.standard_normal((reps, 1))           # component common to all models
    own = rng.standard_normal((reps, n))               # model-specific component
    Z = np.sqrt(r) * shared + np.sqrt(1 - r) * own
    return ndtr(Z)                                     # uniform margins


if __name__ == "__main__":
    R_REP, R_TRUE = 20000, 200000
    rows = []
    for n in (6, 9, 12):
        b = int(np.ceil(n ** (2 / 3)))
        for rho in (0.0, 0.1, 0.2, 0.3):
            true = stats_last_axis(r_dependent_uniform(R_TRUE, n, rho))
            est = subsampling_se(r_dependent_uniform(R_REP, n, rho), b)
            for s in STATS:
                tse = true[s].std(ddof=1)
                rows.append(dict(n=n, b=b, spearman_rho=rho, statistic=s,
                                 true_se=tse, mean_est_se=est[s].mean(),
                                 total_factor=tse / est[s].mean()))
    res = pd.DataFrame(rows)
    base = res[res.spearman_rho == 0].set_index(["n", "statistic"]).total_factor
    res["dependence_factor"] = [
        f / base[(n, s)] for f, n, s in zip(res.total_factor, res.n, res.statistic)]
    res["formula_mean"] = np.where(
        res.statistic == "mean",
        np.sqrt((1 + (res.n - 1) * res.spearman_rho) / (1 - res.spearman_rho)),
        np.nan)
    res.to_csv("NoteS4_simulation_results.csv", index=False)

    pd.set_option("display.width", 200)
    print("Dependence factor (cf. Table S5); mean row also shows the formula:")
    tab = res[res.spearman_rho > 0].pivot_table(
        index=["statistic", "spearman_rho"], columns="n",
        values="dependence_factor").round(2)
    print(tab)
    print("\nFormula (mean):")
    print(res[(res.statistic == "mean") & (res.spearman_rho > 0)]
          .pivot_table(index="spearman_rho", columns="n",
                       values="formula_mean").round(2))
