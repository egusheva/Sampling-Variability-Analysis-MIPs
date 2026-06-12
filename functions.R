estimate_V_exhaustive <- function(x, b) {
  
  n = length(x)
  
  if (b > n){
    stop("b cannot be larger than n. Here b = ", b,
         " and n = ", n)
  }
  
  # Generate all subsample index combinations
  comb_idx = combn(n, b)
  n_sub = ncol(comb_idx)
  
  n_fun = 6
  matrix_results = matrix(nrow = n_sub, ncol = n_fun)
  colnames(matrix_results) <- c("min", "max", "median", "range", "mean", "iqr")
  
  for (i in 1:n_sub){
    x_short = x[ comb_idx[, i] ]
    
    matrix_results[i, "min"]    = min(x_short)
    matrix_results[i, "max"]    = max(x_short)
    matrix_results[i, "median"] = median(x_short)
    matrix_results[i, "range"]  = max(x_short) - min(x_short)
    matrix_results[i, "mean"]   = mean(x_short)
    matrix_results[i, "iqr"]    = IQR(x_short, type = 7)
  }
  
  # Variance estimates using exhaustive subsamples
  V_b = apply(matrix_results, 2, var)
  
  # Scaling ratios (keep your existing logic; extend for mean/iqr)
  ratios = c(
    "min"    = (b / n)^2,
    "max"    = (b / n)^2,
    "median" = (b / n),   # slower convergence
    "range"  = (b / n)^2,
    "mean"   = (b / n),
    "iqr"    = (b / n)
  )
  
  estimates_V  = V_b * ratios
  estimates_se = sqrt(estimates_V)
  
  res = list(
    b = b,
    n = n,
    n_subsamples = n_sub,
    V_b = V_b,
    ratios = ratios,
    estimates_V = estimates_V,
    estimates_se = estimates_se,
    subsample_stats = matrix_results
  )
  
  return(res)
}
