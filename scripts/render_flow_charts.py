#!/usr/bin/env python3
"""Render reproducible CFD charts from exported GitHub event snapshots."""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
STATUSES = ["Done", "Waiting for customer", "Test", "Review", "In Progress", "Ready", "Backlog"]
COLORS = ["#2f855a", "#d69e2e", "#4299e1", "#805ad5", "#dd6b20", "#38a169", "#a0aec0"]


def load(sprint: str):
    with (ROOT / "artifacts" / sprint / "event-cfd.csv").open(encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    times = [datetime.fromisoformat(row["timestamp"]) for row in rows]
    values = [[int(row[status]) for row in rows] for status in STATUSES]
    return times, values


def main() -> None:
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), constrained_layout=True)
    for ax, sprint, title in zip(axes, ["sprint-1", "sprint-2"], ["Sprint 1 CFD", "Sprint 2 CFD · developer WIP = 1"]):
        times, values = load(sprint)
        ax.stackplot(times, values, labels=STATUSES, colors=COLORS, step="post", alpha=0.88)
        ax.set_title(title)
        ax.set_ylabel("Карточка саны")
        ax.set_ylim(bottom=0)
        ax.grid(axis="y", alpha=0.25)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    axes[-1].set_xlabel("29.10.2026 · GitHub event уақыты (UTC)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside right upper")
    fig.suptitle("FitClub ЛЗ9 · GitHub оқиғаларынан алынған CFD", fontsize=15)
    fig.savefig(ROOT / "docs" / "flow" / "cfd-comparison.svg", format="svg")


if __name__ == "__main__":
    main()
