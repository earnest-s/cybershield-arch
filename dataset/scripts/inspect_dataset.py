"""Inspect the downloaded dataset and generate statistics + charts.

Reads dataset/raw/samples.jsonl and produces dataset/docs/dataset_statistics.md
with tables and PNG charts saved under dataset/docs/charts/.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from dataset.scripts.common import DATASET_DIR, setup_logger

RAW_SNAPSHOT = DATASET_DIR / "raw" / "samples.jsonl"
DOCS_DIR = DATASET_DIR / "docs"
CHARTS_DIR = DOCS_DIR / "charts"
STATS_MD = DOCS_DIR / "dataset_statistics.md"

LOG = setup_logger("inspect_dataset")


def load_samples(limit: int | None = None) -> list[dict]:
    if not RAW_SNAPSHOT.exists():
        raise FileNotFoundError(f"Snapshot not found: {RAW_SNAPSHOT}. Run download_dataset.py first.")
    samples: list[dict] = []
    with open(RAW_SNAPSHOT, "r", encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            if limit and len(samples) >= limit:
                break
            if line.strip():
                samples.append(json.loads(line))
    return samples


def _save_chart(fig: plt.Figure, name: str) -> Path:
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    path = CHARTS_DIR / f"{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path.relative_to(DOCS_DIR)


def _bar_chart(counter: Counter, title: str, top_n: int = 15) -> plt.Figure:
    items = counter.most_common(top_n)
    labels = [str(k) for k, _ in items]
    values = [v for _, v in items]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(range(len(labels)), values[::-1])
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels[::-1])
    ax.set_title(title)
    ax.set_xlabel("Count")
    plt.tight_layout()
    return fig


def _pie_chart(counter: Counter, title: str) -> plt.Figure:
    labels = list(counter.keys())
    values = list(counter.values())
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.set_title(title)
    plt.tight_layout()
    return fig


def _histogram(values: list[int], title: str, bins: int = 20) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(values, bins=bins, edgecolor="black")
    ax.set_title(title)
    ax.set_xlabel("Count")
    ax.set_ylabel("Frequency")
    plt.tight_layout()
    return fig


def inspect(samples: list[dict]) -> str:
    if not samples:
        return "# Dataset Statistics\n\nNo samples found."

    # Basic counts
    total = len(samples)
    domains = Counter(s.get("domain", "unknown") for s in samples)
    styles = Counter(s.get("style", "unknown") for s in samples)
    clouds = Counter(s.get("cloud", "unknown") for s in samples)
    complexities = Counter(s.get("target_complexity", "unknown") for s in samples)
    diagram_types = Counter(s.get("diagram_type", "unknown") for s in samples)
    node_counts = [s.get("nodes", 0) for s in samples]
    edge_counts = [s.get("edges", 0) for s in samples]

    # Charts
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    chart_paths = {}
    chart_paths["domains"] = _save_chart(_bar_chart(domains, "Domain Distribution"), "domains")
    chart_paths["styles"] = _save_chart(_bar_chart(styles, "Architecture Style Distribution"), "styles")
    chart_paths["clouds"] = _save_chart(_bar_chart(clouds, "Cloud Provider Distribution"), "clouds")
    chart_paths["complexities"] = _save_chart(_pie_chart(complexities, "Complexity Distribution"), "complexities")
    chart_paths["diagram_types"] = _save_chart(_bar_chart(diagram_types, "Diagram Type Distribution"), "diagram_types")
    chart_paths["node_counts"] = _save_chart(_histogram(node_counts, "Node Count Distribution", bins=30), "node_counts")
    chart_paths["edge_counts"] = _save_chart(_histogram(edge_counts, "Edge Count Distribution", bins=30), "edge_counts")

    # Largest / smallest by node count
    if node_counts:
        max_idx = max(range(len(node_counts)), key=lambda i: node_counts[i])
        min_idx = min(range(len(node_counts)), key=lambda i: node_counts[i])
        largest = samples[max_idx]
        smallest = samples[min_idx]

    lines = [
        "# Dataset Statistics",
        "",
        f"**Source:** ajibawa-2023/Technical-Architectures-Large",
        f"**Total Samples Analyzed:** {total:,}",
        "",
        "## Domain Distribution",
        "",
        *[f"- **{k}**: {v:,}" for k, v in domains.most_common()],
        "",
        f"![Domain Distribution]({chart_paths['domains']})",
        "",
        "## Architecture Style Distribution",
        "",
        *[f"- **{k}**: {v:,}" for k, v in styles.most_common()],
        "",
        f"![Style Distribution]({chart_paths['styles']})",
        "",
        "## Cloud Provider Distribution",
        "",
        *[f"- **{k}**: {v:,}" for k, v in clouds.most_common()],
        "",
        f"![Cloud Distribution]({chart_paths['clouds']})",
        "",
        "## Complexity Distribution",
        "",
        *[f"- **{k}**: {v:,}" for k, v in complexities.most_common()],
        "",
        f"![Complexity Distribution]({chart_paths['complexities']})",
        "",
        "## Diagram Type Distribution",
        "",
        *[f"- **{k}**: {v:,}" for k, v in diagram_types.most_common()],
        "",
        f"![Diagram Type Distribution]({chart_paths['diagram_types']})",
        "",
        "## Node Count Distribution",
        "",
        f"- **Mean**: {sum(node_counts)/len(node_counts):.1f}",
        f"- **Median**: {sorted(node_counts)[len(node_counts)//2]}",
        f"- **Max**: {max(node_counts)} (sample id {largest.get('id')})",
        f"- **Min**: {min(node_counts)} (sample id {smallest.get('id')})",
        "",
        f"![Node Count Histogram]({chart_paths['node_counts']})",
        "",
        "## Edge Count Distribution",
        "",
        f"- **Mean**: {sum(edge_counts)/len(edge_counts):.1f}",
        f"- **Median**: {sorted(edge_counts)[len(edge_counts)//2]}",
        f"- **Max**: {max(edge_counts)}",
        f"- **Min**: {min(edge_counts)}",
        "",
        f"![Edge Count Histogram]({chart_paths['edge_counts']})",
        "",
        "## Largest Architecture",
        "",
        f"- **Sample ID**: {largest.get('id')}",
        f"- **Domain**: {largest.get('domain')}",
        f"- **Style**: {largest.get('style')}",
        f"- **Nodes (source)**: {largest.get('nodes')}",
        f"- **Edges (source)**: {largest.get('edges')}",
        f"- **Constraints**: {largest.get('constraints')}",
        "",
        "## Smallest Architecture",
        "",
        f"- **Sample ID**: {smallest.get('id')}",
        f"- **Domain**: {smallest.get('domain')}",
        f"- **Style**: {smallest.get('style')}",
        f"- **Nodes (source)**: {smallest.get('nodes')}",
        f"- **Edges (source)**: {smallest.get('edges')}",
        f"- **Constraints**: {smallest.get('constraints')}",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate dataset statistics and charts.")
    parser.add_argument("--limit", type=int, default=None, help="Limit samples to process (for quick runs).")
    args = parser.parse_args()
    try:
        samples = load_samples(args.limit)
        md = inspect(samples)
        DOCS_DIR.mkdir(parents=True, exist_ok=True)
        STATS_MD.write_text(md, encoding="utf-8")
        LOG.info("Statistics written to %s", STATS_MD)
        return 0
    except Exception as e:
        LOG.exception("Inspection failed: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())