"""
Figures 1-3 of the paper, made from the files in source_data/.

Run from the repository root:
    python make_figures.py
Writes Figure_1.svg, Figure_2.svg and Figure_3.svg.

Source data:
  source_data/Figure1_source_data.csv  coding of the 30 reviewed studies (Table S4)
  source_data/Figure2_source_data.csv  relative standard error (RSE) of each statistic
  source_data/Figure3_source_data.csv  full-ensemble min/max/median with standard errors,
                                       and the individual model projections
Requires pandas, numpy, matplotlib and seaborn.
"""
import textwrap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
from matplotlib.lines import Line2D

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans"]

BG, GRID = "#F7F7F7", "#D0D0D0"
TITLE_BOX = dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.3")


def style_axes(ax):
    ax.set_facecolor(BG)
    ax.grid(True, color=GRID, linewidth=0.6, alpha=0.7)
    for spine in ax.spines.values():
        spine.set_color("black")
        spine.set_linewidth(1.0)


# =============================================================================
# Figure 1 - review of 30 intercomparison studies
# =============================================================================
def figure_1():
    df = pd.read_csv("source_data/Figure1_source_data.csv")

    # Codes in Table S4 -> labels shown in the figure
    df["centrality"] = np.where(df["reported_outputs"].str.contains("CM"),
                                "Centrality measure reported",
                                "No centrality measure reported")
    panels = [
        ("Emphasis of quantitative vs qualitative findings", "emphasis_quantitative_qualitative",
         {"I": "Qualitative findings emphasized", "P": "Quantitative findings emphasized", "M": "Mixed"}),
        ("Ensemble choice justification", "ensemble_choice_justification",
         {"DM": "Models are different", "EM": "Well-established models",
          "MP": "Models are part of a funded project"}),
        ("Study emphasis", "emphasis_similarities_differences",
         {"S": "Focus on similarities", "D": "Focus on differences"}),
        ("Reported statistics", "centrality", None),
        ("Input parameter harmonization", "parameter_harmonization",
         {"EL": "Existing but limited", "NE": "Non-existing"}),
    ]
    colors = sns.color_palette("Set2", n_colors=len(panels))

    fig, axes = plt.subplots(3, 2, figsize=(17, 18))
    axes = axes.flatten()

    # A - histogram of ensemble sizes
    ax = axes[0]
    sizes = df["ensemble_size"]
    bins = np.arange(1, sizes.max() + 2)
    centers = bins[:-1] + 0.5
    ax.hist(sizes, bins=bins, color="#4C72B0", edgecolor="black")
    ax.set_xticks(centers[::2])
    ax.set_xticklabels(bins[:-1][::2], fontsize=20, color="grey")
    ax.set_title("Model ensemble size", fontsize=22, pad=22, bbox=TITLE_BOX)
    ax.set_facecolor(BG)
    ax.grid(True, color=GRID, linewidth=0.6, alpha=0.7)
    ax.tick_params(axis="y", labelsize=20, colors="grey")
    ax.set_xlabel("Ensemble size", fontsize=18)
    ax.set_ylabel("Number of studies", fontsize=18)
    ax.text(-0.35, 1.12, "A", transform=ax.transAxes, fontsize=26, fontweight="bold", va="top")

    # B-F - lollipop plots
    for i, ((title, col, labels), color) in enumerate(zip(panels, colors), start=1):
        ax = axes[i]
        values = df[col].map(labels) if labels else df[col]
        counts = values.value_counts()                      # largest first
        y = np.arange(len(counts))
        ax.hlines(y, 0, counts.values, color=color, linewidth=14)
        ax.plot(counts.values, y, "o", color=color, markersize=20)
        ax.set_yticks(y)
        ax.set_yticklabels(["\n".join(textwrap.wrap(c, 22)) for c in counts.index])
        ax.set_ylim(len(counts) - 0.2, -0.8)
        ax.set_title(title, fontsize=22, pad=22, bbox=TITLE_BOX)
        style_axes(ax)
        ax.tick_params(axis="y", labelsize=20, pad=4, colors="black")
        ax.tick_params(axis="x", labelsize=20, colors="grey")
        ax.xaxis.set_major_locator(mtick.MaxNLocator(integer=True))
        ax.set_xlabel("Number of studies", fontsize=18)
        ax.set_xlim(0, 30)
        ax.text(-0.35, 1.12, "ABCDEF"[i], transform=ax.transAxes,
                fontsize=26, fontweight="bold", va="top")

    plt.subplots_adjust(left=0.10, right=0.97, top=0.95, bottom=0.05, hspace=0.45, wspace=0.50)
    fig.savefig("Figure_1.svg", format="svg", dpi=300, bbox_inches="tight")
    plt.close(fig)


# =============================================================================
# Figure 2 - distribution of the relative standard error per statistic
# =============================================================================
def figure_2():
    df = pd.read_csv("source_data/Figure2_source_data.csv")
    # Values shown in the figure: near-zero minima/medians omitted (empty),
    # RSE above 100% shown at 100%.
    df = df.dropna(subset=["RSE_shown_in_figure_percent"]).copy()
    df["RSE"] = df["RSE_shown_in_figure_percent"] / 100
    names = {"iqr": "IQR", "max": "Maximum", "mean": "Mean",
             "median": "Median", "min": "Minimum", "range": "Range"}
    df["Measure"] = df["statistic"].map(names)
    order = ["IQR", "Maximum", "Mean", "Median", "Minimum", "Range"]
    colors = {"Minimum": "#7e027e", "Maximum": "#d7a320", "Median": "#cb6208",
              "Range": "#2e79b6", "IQR": "#1b9e77", "Mean": "#c44e52"}

    fig, ax = plt.subplots(figsize=(14, 8))
    sns.violinplot(data=df, x="Measure", y="RSE", hue="Measure", order=order,
                   dodge=False, inner="quartile", bw_adjust=1.0, linewidth=1.2,
                   palette=colors, legend=False, ax=ax)
    style_axes(ax)

    n_per_measure = df["Measure"].value_counts()
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels(order, rotation=45, ha="right")
    for x, m in enumerate(order):
        ax.text(x, -0.15, f"n = {n_per_measure[m]}", transform=ax.get_xaxis_transform(),
                ha="center", va="top", fontsize=16, color="grey")

    ax.tick_params(axis="both", labelsize=16, colors="grey")
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax.set_ylim(0, 1)
    ax.set_ylabel("Relative Standard Error (%)", fontsize=24, color="black")
    ax.set_xlabel("")

    plt.subplots_adjust(left=0.10, right=0.98, top=0.95, bottom=0.25)
    fig.savefig("Figure_2.svg", format="svg", dpi=300, bbox_inches="tight")
    plt.close(fig)


# =============================================================================
# Figure 3 - original vs alternative ensembles, two illustrative examples
# =============================================================================
def figure_3():
    df = pd.read_csv("source_data/Figure3_source_data.csv")
    panels = [("A", "ENGAGE-B"), ("B", "ECEMF-P")]
    COL_MAIN, COL_SE = "#6958cc", "#cdce0b"
    off_main, off_se = -0.14, 0.14
    rng = np.random.default_rng(1)                  # reproducible jitter

    fig, axes = plt.subplots(1, 2, figsize=(16, 7.5))
    for ax, (panel, label) in zip(axes, panels):
        sub = df[df["panel"] == panel]
        pts = sub[sub["element"] == "individual model projection"]
        stats = sub[sub["element"] != "individual model projection"]
        carriers = sorted(stats["carrier"].unique())
        x = np.arange(len(carriers))

        def get(stat):
            s = stats[stats["element"] == f"full-ensemble {stat}"].set_index("carrier").reindex(carriers)
            return s["value_EJ"].to_numpy(), s["standard_error_EJ"].fillna(0).to_numpy()

        mn, mn_se = get("min")
        mx, mx_se = get("max")
        md, md_se = get("median")

        # Original ensemble: range, individual projections, median
        ax.vlines(x + off_main, mn, mx, color=COL_MAIN, linewidth=2.0, alpha=0.9, zorder=4)
        n_per_carrier = []
        for xi, c in zip(x, carriers):
            v = pts.loc[pts["carrier"] == c, "value_EJ"].to_numpy()
            n_per_carrier.append(len(v))
            ax.scatter(xi + off_main + rng.uniform(-0.05, 0.05, len(v)), v, s=22,
                       facecolors="white", edgecolors=COL_MAIN, linewidths=1.0, zorder=5)
        ax.scatter(x + off_main, md, color=COL_MAIN, s=80, edgecolors="white",
                   linewidths=1.0, zorder=6)

        # Alternative ensembles: min - SE to max + SE, and median +/- SE
        ax.vlines(x + off_se, mn - mn_se, mx + mx_se, color=COL_SE, linewidth=2.0, alpha=0.9, zorder=3)
        for xi, lo, hi in zip(x + off_se, md - md_se, md + md_se):
            ax.plot([xi, xi], [lo, hi], color=COL_SE, linewidth=12, alpha=0.9,
                    solid_capstyle="round", zorder=5)

        n_models = pts["model"].nunique()
        ax.set_title(f"{label} (n={n_models})", fontsize=18, pad=14, bbox=TITLE_BOX)
        ax.set_ylabel("Exajoules", fontsize=14)
        style_axes(ax)
        ax.set_xticks(x)
        ax.set_xticklabels([f"{c}\n(n={k})" for c, k in zip(carriers, n_per_carrier)],
                           rotation=45, ha="right", fontsize=12, color="grey")
        ax.tick_params(axis="y", labelsize=13, colors="grey")
        ax.text(-0.08, 1.18, panel, transform=ax.transAxes, ha="left", va="top",
                fontsize=26, fontweight="bold")

    legend = [
        Line2D([0], [0], color=COL_MAIN, lw=2.8, label="Original ensemble: range"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COL_MAIN,
               markeredgecolor="white", markersize=10, label="Original ensemble: median"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor="white",
               markeredgecolor=COL_MAIN, markersize=6, label="Individual model projections"),
        Line2D([0], [0], color=COL_SE, lw=2.8, label="Alternative ensembles"),
    ]
    fig.legend(handles=legend, fontsize=13, loc="lower center", ncol=4,
               frameon=False, bbox_to_anchor=(0.5, 0.0))
    plt.subplots_adjust(left=0.06, right=0.98, top=0.95, bottom=0.22, wspace=0.25)
    fig.savefig("Figure_3.svg", format="svg", dpi=300, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    figure_1()
    figure_2()
    figure_3()
    print("Saved Figure_1.svg, Figure_2.svg and Figure_3.svg")
