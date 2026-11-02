"""
analysis.py
------------
Performs a complete analysis of student marks loaded from students.csv:

1. Loads data and checks for missing values
2. Validates marks (clips to 0–100 range)
3. Calculates Total Marks, Percentage, and Grade for each student
4. Computes class-level statistics (average, highest/lowest scorer, etc.)
5. Computes subject-wise statistics
6. Saves enriched data to results.csv
7. Generates six publication-quality charts and saves them in charts/ folder

Usage:
    python analysis.py
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")                # Use non-interactive backend (safe for servers)
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

# ── File Paths ───────────────────────────────────────────────────────
INPUT_FILE = "students.csv"
OUTPUT_FILE = "results.csv"
CHARTS_DIR = "charts"

# Subjects list (must match CSV column names)
SUBJECTS = ["Maths", "Science", "English", "History", "Computer"]

# Grade boundaries: (lower_bound, label)
# Checked top-down, so 90+ is matched first
GRADE_BOUNDARIES = [
    (90, "A+"),
    (80, "A"),
    (70, "B"),
    (60, "C"),
    (50, "D"),
    (0,  "F"),
]


# ═══════════════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

def assign_grade(percentage: float) -> str:
    """
    Return a letter grade based on the percentage.

    Grade scale:
        90+     → A+
        80–89.99 → A
        70–79.99 → B
        60–69.99 → C
        50–59.99 → D
        Below 50 → F (Fail)
    """
    for lower, grade in GRADE_BOUNDARIES:
        if percentage >= lower:
            return grade
    return "F"  # Fallback (should not reach here)


# ═══════════════════════════════════════════════════════════════════════
#  CORE ANALYSIS
# ═══════════════════════════════════════════════════════════════════════

def load_and_validate(filepath: str) -> pd.DataFrame:
    """
    Load the CSV file and perform basic validation.

    Steps:
        - Read CSV into a DataFrame
        - Report missing values
        - Fill missing marks with 0
        - Clip marks to the valid range [0, 100]
    """
    if not os.path.exists(filepath):
        print(f"[ERROR] '{filepath}' not found. Run generate_data.py first.")
        sys.exit(1)

    df = pd.read_csv(filepath)
    print(f"[LOADED] '{filepath}' -- {len(df)} rows, {len(df.columns)} columns.\n")

    # ── Check for missing values ─────────────────────────────────────
    missing = df.isnull().sum()
    total_missing = missing.sum()
    if total_missing > 0:
        print("[WARNING] Missing values detected:")
        print(missing[missing > 0])
        # Fill missing marks with 0
        for subject in SUBJECTS:
            df[subject] = df[subject].fillna(0)
        print("   -> Missing marks filled with 0.\n")
    else:
        print("[OK] No missing values found.\n")

    # ── Clip marks to [0, 100] ───────────────────────────────────────
    for subject in SUBJECTS:
        original = df[subject].copy()
        df[subject] = df[subject].clip(0, 100)
        clipped_count = (original != df[subject]).sum()
        if clipped_count > 0:
            print(f"[WARNING] {clipped_count} value(s) in '{subject}' were outside 0-100 and have been clipped.")

    return df


def compute_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add Total, Percentage, and Grade columns to the DataFrame.
    """
    df["Total"] = df[SUBJECTS].sum(axis=1)                     # Sum of 5 subjects (max 500)
    df["Percentage"] = (df["Total"] / 500 * 100).round(2)      # Percentage out of 500
    df["Grade"] = df["Percentage"].apply(assign_grade)          # Letter grade
    return df


def class_statistics(df: pd.DataFrame) -> dict:
    """
    Compute and return class-level statistics as a dictionary.
    """
    stats = {}

    # ── Class average ────────────────────────────────────────────────
    stats["avg_total"] = round(df["Total"].mean(), 2)
    stats["avg_percentage"] = round(df["Percentage"].mean(), 2)
    stats["subject_averages"] = {subj: round(df[subj].mean(), 2) for subj in SUBJECTS}

    # ── Highest scorer ───────────────────────────────────────────────
    top = df.loc[df["Total"].idxmax()]
    stats["highest"] = {
        "name": top["Name"],
        "total": int(top["Total"]),
        "percentage": float(top["Percentage"]),
    }

    # ── Lowest scorer ────────────────────────────────────────────────
    bottom = df.loc[df["Total"].idxmin()]
    stats["lowest"] = {
        "name": bottom["Name"],
        "total": int(bottom["Total"]),
        "percentage": float(bottom["Percentage"]),
    }

    # ── Grade distribution ───────────────────────────────────────────
    grade_order = ["A+", "A", "B", "C", "D", "F"]
    stats["grade_counts"] = (
        df["Grade"]
        .value_counts()
        .reindex(grade_order, fill_value=0)
    )

    # ── Pass percentage (grade != F → pass) ──────────────────────────
    pass_count = (df["Grade"] != "F").sum()
    stats["pass_percentage"] = round(pass_count / len(df) * 100, 2)

    # ── Subject-wise details ─────────────────────────────────────────
    subject_stats = {}
    for subj in SUBJECTS:
        subject_stats[subj] = {
            "highest": int(df[subj].max()),
            "lowest": int(df[subj].min()),
            "average": round(df[subj].mean(), 2),
        }
    stats["subject_stats"] = subject_stats

    return stats


def print_statistics(stats: dict):
    """Pretty-print the class statistics to the console."""
    print("=" * 60)
    print("           CLASS STATISTICS")
    print("=" * 60)

    print(f"\n[AVG] Class Average Total : {stats['avg_total']} / 500")
    print(f"[AVG] Class Average %     : {stats['avg_percentage']}%")

    print(f"\n[1st] Highest Scorer : {stats['highest']['name']} "
          f"({stats['highest']['total']}/500, {stats['highest']['percentage']}%)")
    print(f"[Last] Lowest Scorer  : {stats['lowest']['name']} "
          f"({stats['lowest']['total']}/500, {stats['lowest']['percentage']}%)")

    print(f"\n[PASS] Pass Percentage : {stats['pass_percentage']}%")

    print("\n[SUBJECTS] Subject-wise Averages:")
    for subj, avg in stats["subject_averages"].items():
        print(f"   {subj:10s} -> {avg}")

    print("\n[GRADES] Grade Distribution:")
    for grade, count in stats["grade_counts"].items():
        print(f"   {grade:3s} -> {count} student(s)")

    print("\n[DETAILS] Subject-wise Details:")
    for subj, info in stats["subject_stats"].items():
        print(f"   {subj:10s} | High: {info['highest']:3d} | "
              f"Low: {info['lowest']:3d} | Avg: {info['average']:.2f}")

    print("=" * 60)


# ═══════════════════════════════════════════════════════════════════════
#  CHART GENERATION
# ═══════════════════════════════════════════════════════════════════════

def ensure_charts_dir():
    """Create the charts/ folder if it does not exist."""
    os.makedirs(CHARTS_DIR, exist_ok=True)


def chart_grade_bar(stats: dict):
    """Bar chart: Number of students in each grade category."""
    grades = stats["grade_counts"]
    colors = ["#2ecc71", "#27ae60", "#3498db", "#f39c12", "#e67e22", "#e74c3c"]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(grades.index, grades.values, color=colors, edgecolor="black", linewidth=0.5)

    # Add count labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height + 0.3,
                str(int(height)), ha="center", va="bottom", fontweight="bold")

    ax.set_title("Number of Students in Each Grade", fontsize=14, fontweight="bold")
    ax.set_xlabel("Grade", fontsize=12)
    ax.set_ylabel("Number of Students", fontsize=12)
    ax.set_ylim(0, max(grades.values) + 3)
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "grade_bar_chart.png"), dpi=150)
    plt.close()
    print("   [OK] grade_bar_chart.png")


def chart_grade_pie(stats: dict):
    """Pie chart: Grade distribution."""
    grades = stats["grade_counts"]
    # Only include grades that have at least 1 student
    non_zero = grades[grades > 0]
    colors = ["#2ecc71", "#27ae60", "#3498db", "#f39c12", "#e67e22", "#e74c3c"]
    used_colors = [colors[list(grades.index).index(g)] for g in non_zero.index]

    fig, ax = plt.subplots(figsize=(7, 7))
    wedges, texts, autotexts = ax.pie(
        non_zero.values,
        labels=non_zero.index,
        autopct="%1.1f%%",
        colors=used_colors,
        startangle=140,
        textprops={"fontsize": 11},
    )
    for autotext in autotexts:
        autotext.set_fontweight("bold")

    ax.set_title("Grade Distribution", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "grade_pie_chart.png"), dpi=150)
    plt.close()
    print("   [OK] grade_pie_chart.png")


def chart_subject_average(stats: dict):
    """Bar chart: Subject-wise class average."""
    subjects = list(stats["subject_averages"].keys())
    averages = list(stats["subject_averages"].values())
    colors = sns.color_palette("viridis", len(subjects))

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(subjects, averages, color=colors, edgecolor="black", linewidth=0.5)

    for bar, avg in zip(bars, averages):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f"{avg:.1f}", ha="center", va="bottom", fontweight="bold", fontsize=10)

    ax.set_title("Subject-wise Class Average", fontsize=14, fontweight="bold")
    ax.set_xlabel("Subject", fontsize=12)
    ax.set_ylabel("Average Marks", fontsize=12)
    ax.set_ylim(0, 100)
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "subject_average_chart.png"), dpi=150)
    plt.close()
    print("   [OK] subject_average_chart.png")


def chart_percentage_histogram(df: pd.DataFrame):
    """Histogram: Distribution of student percentages."""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(df["Percentage"], bins=10, color="#3498db", edgecolor="black", linewidth=0.5)

    ax.set_title("Distribution of Student Percentages", fontsize=14, fontweight="bold")
    ax.set_xlabel("Percentage (%)", fontsize=12)
    ax.set_ylabel("Number of Students", fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "percentage_histogram.png"), dpi=150)
    plt.close()
    print("   [OK] percentage_histogram.png")


def chart_top5(df: pd.DataFrame):
    """Bar chart: Top 5 students by percentage."""
    top5 = df.nlargest(5, "Percentage")
    colors = ["#f1c40f", "#bdc3c7", "#cd7f32", "#3498db", "#9b59b6"]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(top5["Name"], top5["Percentage"], color=colors, edgecolor="black", linewidth=0.5)

    for bar, pct in zip(bars, top5["Percentage"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f"{pct:.1f}%", ha="center", va="bottom", fontweight="bold", fontsize=10)

    ax.set_title("Top 5 Students by Percentage", fontsize=14, fontweight="bold")
    ax.set_xlabel("Student Name", fontsize=12)
    ax.set_ylabel("Percentage (%)", fontsize=12)
    ax.set_ylim(0, 105)
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "top5_students_chart.png"), dpi=150)
    plt.close()
    print("   [OK] top5_students_chart.png")


def chart_subject_box(df: pd.DataFrame):
    """Box plot: Marks distribution per subject (bonus chart)."""
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(data=df[SUBJECTS], palette="Set2", ax=ax)

    ax.set_title("Subject-wise Marks Distribution", fontsize=14, fontweight="bold")
    ax.set_xlabel("Subject", fontsize=12)
    ax.set_ylabel("Marks", fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "subject_box_plot.png"), dpi=150)
    plt.close()
    print("   [OK] subject_box_plot.png")


# ═══════════════════════════════════════════════════════════════════════
#  MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════

def run_analysis(filepath: str = INPUT_FILE):
    """
    Run the full analysis pipeline and return (DataFrame, stats_dict).

    This function is also called by app.py so the Streamlit dashboard
    can reuse the same logic.
    """
    # Step 1 – Load & validate
    df = load_and_validate(filepath)

    # Step 2 – Compute Total, Percentage, Grade
    df = compute_metrics(df)

    # Step 3 – Compute class statistics
    stats = class_statistics(df)

    return df, stats


def main():
    """CLI entry point: runs analysis, prints stats, saves results & charts."""
    df, stats = run_analysis()

    # Print statistics to console
    print_statistics(stats)

    # Save enriched DataFrame to results.csv
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n[SAVED] Results saved to '{OUTPUT_FILE}'.")

    # Generate all charts
    ensure_charts_dir()
    print("\n[CHARTS] Generating charts...")
    chart_grade_bar(stats)
    chart_grade_pie(stats)
    chart_subject_average(stats)
    chart_percentage_histogram(df)
    chart_top5(df)
    chart_subject_box(df)
    print(f"\n[DONE] All charts saved to '{CHARTS_DIR}/' folder.")


if __name__ == "__main__":
    main()
