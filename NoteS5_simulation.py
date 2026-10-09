"""
Note S5 - Accuracy of subsampling standard errors at the ensemble sizes used.

For n = 6, 9 and 12, draw synthetic ensembles from distributions on [0, 1] with
known minimum, maximum, median and range, apply the same subsampling estimator
as the analysis (functions.R: all subsets of size b = ceil(n^(2/3)), sample
variance across subsets, rescaled by (b/n)^2 for min/max/range and b/n for
median/mean/IQR), and compare with the true standard errors.

Output: NoteS5_simulation_results.csv (one row per distribution x n x statistic)
  true_se      SD of the statistic over R_TRUE independent ensembles of size n
  mean_est_se  average subsampling SE over R_REP synthetic ensembles
  ratio        mean_est_se / true_se (Table S6 reports the range across distributions)
  ratio_p10/90 10th and 90th percentiles of est_se / true_se
  coverage_95  share of ensembles where |statistic - true value| <= 1.96 * est_se

Requires numpy, scipy, pandas. Runtime: a few minutes.
"""
import itertools
import numpy as np
import pandas as pd
from scipy.stats import truncnorm

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
    sub = stats_last_axis(X[:, idx])                    # each: (reps, n_subsets)
    return {s: np.sqrt(sub[s].var(axis=1, ddof=1) * (b / n) ** RATIO_POW[s])
            for s in STATS}


def rtnorm(k, mu=0.5, s=0.25):
    """Normal(mu, s) truncated to [0, 1]."""
    return truncnorm.rvs((0 - mu) / s, (1 - mu) / s, loc=mu, scale=s,
                         size=k, random_state=rng)


def rtexp(k, rate=3.0):
    """Exponential(rate) truncated to [0, 1] (right-skewed)."""
    u = rng.random(k)
    return -np.log(1 - u * (1 - np.exp(-rate))) / rate


DISTS = {"Uniform": lambda k: rng.random(k),
         "Truncated normal": rtnorm,
         "Truncated exponential": rtexp}

if __name__ == "__main__":
    R_REP, R_TRUE = 5000, 200000
    rows = []
    for dname, rd in DISTS.items():
        big = rd(2_000_000)
        q1, med, q3 = np.percentile(big, [25, 50, 75])
        theta = {"min": 0.0, "max": 1.0, "median": med, "range": 1.0,
                 "mean": big.mean(), "iqr": q3 - q1}
        for n in (6, 9, 12):
            b = int(np.ceil(n ** (2 / 3)))
            true = stats_last_axis(rd(R_TRUE * n).reshape(R_TRUE, n))
            X = rd(R_REP * n).reshape(R_REP, n)
            full = stats_last_axis(X)
            est = subsampling_se(X, b)
            for s in STATS:
                tse = true[s].std(ddof=1)
                r = est[s] / tse
                rows.append(dict(
                    distribution=dname, n=n, b=b, statistic=s,
                    true_se=tse, mean_est_se=est[s].mean(),
                    ratio=est[s].mean() / tse,
                    ratio_p10=np.quantile(r, .1), ratio_p90=np.quantile(r, .9),
                    coverage_95=np.mean(np.abs(full[s] - theta[s]) <= 1.96 * est[s])))
    res = pd.DataFrame(rows)
    res.to_csv("NoteS5_simulation_results.csv", index=False)
    pd.set_option("display.width", 200)
    print(res.round(2).to_string(index=False))
