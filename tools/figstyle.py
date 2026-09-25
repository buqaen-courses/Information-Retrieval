"""Shared matplotlib style for ALL session images.

Import with: from tools.figstyle import apply_style
All make_images.py scripts must call apply_style() first for consistent
fonts/colors/sizes. Deterministic: no random state here.
"""
import matplotlib as mpl
import matplotlib.pyplot as plt


def apply_style() -> None:
    """Apply the course-wide figure style."""
    mpl.rcParams.update(
        {
            "figure.figsize": (8, 4.5),
            "figure.dpi": 150,
            "savefig.dpi": 150,
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.labelsize": 10,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 9,
            "axes.grid": True,
            "grid.alpha": 0.3,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


COLORS = {
    "primary": "#1f77b4",
    "accent": "#ff7f0e",
    "ok": "#2ca02c",
    "warn": "#d62728",
    "neutral": "#7f7f7f",
}
