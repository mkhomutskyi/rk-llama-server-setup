"""Render original article figures from the aggregate benchmark CSV."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
with (ASSETS / "metrics.csv").open(newline="", encoding="utf-8") as stream:
    rows = list(csv.DictReader(stream))
colors = ["#2877b5", "#f0ce3b", "#289d91"]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12,
                     "figure.facecolor": "white", "axes.facecolor": "white"})

for key, title in [("generation_tps", "GENERATING THE REPLY"),
                   ("prompt_tps", "PROCESSING THE PROMPT")]:
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5))
    fig.suptitle(title, color="#1764a2", weight="bold", fontsize=22, y=.98)
    for ax, model in zip(axes, dict.fromkeys(row["model"] for row in rows)):
        selected = [row for row in rows if row["model"] == model]
        values = [float(row[key]) for row in selected]
        ax.barh(["CPU", "NPU + CPU", "GPU + CPU"], values, color=colors,
                edgecolor="#222222", linewidth=1.3, height=.55)
        ax.invert_yaxis()
        ax.set_xlim(0, max(values) * 1.27)
        ax.set_title(model, fontsize=14, pad=15)
        ax.set_xlabel("Tokens per second (higher is faster)", fontsize=11)
        for index, value in enumerate(values):
            ax.text(value + max(values) * .035, index, f"{value:.2f}", va="center",
                    weight="bold", fontsize=13)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.tick_params(axis="y", length=0)
    fig.text(.5, .02, "Orange Pi 5 / 16 GB | 4 big-core threads | 2 short repeats | 14 Oct 2026\n"
             "Gemma pp64/tg32; Qwen pp32/tg16. Qwen jobs capped at 14 GiB. Not a universal ranking.",
             ha="center", fontsize=10, color="#555555")
    fig.tight_layout(rect=(0, .10, 1, .90), w_pad=3)
    fig.savefig(ASSETS / ("generation.png" if key == "generation_tps" else "prompt.png"), dpi=160)
    plt.close(fig)

fig, ax = plt.subplots(figsize=(12, 6))
ax.set(xlim=(0, 12), ylim=(0, 6)); ax.axis("off")
ax.text(6, 5.6, "ONE AI BOX. THREE BACKEND CHOICES.", ha="center",
        color="#1764a2", fontsize=21, weight="bold")
def box(x, y, width, height, title, detail, color="#eef5fb"):
    ax.add_patch(Rectangle((x, y), width, height, edgecolor="#222222",
                           facecolor=color, linewidth=1.6))
    ax.text(x+width/2, y+height*.65, title, ha="center", fontsize=14, weight="bold")
    ax.text(x+width/2, y+height*.26, detail, ha="center", fontsize=11)
def arrow(start, end):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="->", mutation_scale=18,
                                color="#777777", linewidth=1.6))
box(.2, 3.4, 2.6, 1, "Your browser", "Trusted LAN")
box(3.6, 3.4, 3, 1, "Open WebUI", "Docker / port 3000")
box(7.4, 3.4, 4.2, 1, "rk-llama.cpp", "Native / localhost:11436")
arrow((2.8, 3.9), (3.6, 3.9)); arrow((6.6, 3.9), (7.4, 3.9))
for x, title, detail, color in [(2, "CPU", "Separate CPU-only build", "#eef5fb"),
                              (5.2, "NPU + CPU", "RKNPU2 backend", "#fff3b4"),
                              (8.4, "GPU + CPU", "Vendor Mali Vulkan", "#e8f6f2")]:
    box(x, 1.2, 2.8, 1, title, detail, color)
    arrow((9.5, 3.4), (x+1.4, 2.2))
ax.text(6, .55, "Same GGUF files on NVMe. Select one backend at a time.", ha="center", fontsize=13)
fig.tight_layout(); fig.savefig(ASSETS / "architecture.png", dpi=160); plt.close(fig)
print("Rendered architecture.png, generation.png and prompt.png")
