"""
app.py - Student Performance Analysis Dashboard (Streamlit)

All tables, metrics and charts are generated LIVE from the data
(default: students.csv, or any CSV uploaded from the sidebar).
No static PNG images are used.

Run with:  streamlit run app.py
"""

import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

# ------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------
SUBJECTS = ["Maths", "Science", "English", "History", "Computer"]
REQUIRED_COLUMNS = ["Student_ID", "Name"] + SUBJECTS
MAX_TOTAL = 100 * len(SUBJECTS)          # 500
GRADE_ORDER = ["A+", "A", "B", "C", "D", "F"]
GRADE_COLORS = {
    "A+": "#2e7d32", "A": "#66bb6a", "B": "#42a5f5",
    "C": "#ffca28", "D": "#ffa726", "F": "#ef5350",
}
PASS_PERCENTAGE = 50

sns.set_theme(style="whitegrid")


# ------------------------------------------------------------------
# Data loading and analysis
# ------------------------------------------------------------------
def assign_grade(percentage_series):
    """Convert a Series of percentages into grade labels."""
    bins = [-float("inf"), 50, 60, 70, 80, 90, float("inf")]
    labels = ["F", "D", "C", "B", "A", "A+"]
    # right=False -> intervals like [90, inf) so exactly 90 gives A+
    return pd.cut(percentage_series, bins=bins, labels=labels, right=False)


def clean_data(df):
    """
    Validate and clean the raw data.
    Returns (clean_df, list_of_warning_messages).
    """
    warnings = []

    # 1. Required columns must exist
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        raise ValueError(f"CSV is missing required columns: {', '.join(missing_cols)}")

    df = df[REQUIRED_COLUMNS].copy()

    # 2. Convert marks to numbers (text like 'abc' becomes NaN)
    for subject in SUBJECTS:
        df[subject] = pd.to_numeric(df[subject], errors="coerce")

    # 3. Marks outside 0-100 are invalid -> treat as missing
    out_of_range = ((df[SUBJECTS] < 0) | (df[SUBJECTS] > 100)).any(axis=1)
    if out_of_range.any():
        warnings.append(f"{out_of_range.sum()} row(s) had marks outside 0-100 and were removed.")
        df.loc[out_of_range, SUBJECTS] = float("nan")

    # 4. Drop rows with any missing marks or missing name
    bad_rows = df[SUBJECTS].isnull().any(axis=1) | df["Name"].isnull()
    if bad_rows.any():
        warnings.append(f"{bad_rows.sum()} row(s) with missing/invalid values were removed.")
        df = df[~bad_rows]

    if df.empty:
        raise ValueError("No valid rows left after cleaning the data.")

    return df.reset_index(drop=True), warnings


def calculate_results(df):
    """Add Total, Percentage and Grade columns."""
    df = df.copy()
    df["Total"] = df[SUBJECTS].sum(axis=1)
    df["Percentage"] = (df["Total"] / MAX_TOTAL * 100).round(2)
    df["Grade"] = assign_grade(df["Percentage"]).astype(str)
    return df


@st.cache_data
def load_and_process(file_or_path):
    """Read the CSV, clean it, calculate results. Cached for speed."""
    raw = pd.read_csv(file_or_path)
    clean, warnings = clean_data(raw)
    return calculate_results(clean), warnings


# ------------------------------------------------------------------
# Chart functions (each returns a Matplotlib figure built from data)
# ------------------------------------------------------------------
def chart_grade_bar(df):
    counts = df["Grade"].value_counts().reindex(GRADE_ORDER, fill_value=0)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(counts.index, counts.values, color=[GRADE_COLORS[g] for g in counts.index])
    for i, v in enumerate(counts.values):
        ax.text(i, v + 0.1, str(v), ha="center", fontweight="bold")
    ax.set_title("Number of Students in Each Grade")
    ax.set_xlabel("Grade")
    ax.set_ylabel("Number of Students")
    fig.tight_layout()
    return fig


def chart_grade_pie(df):
    counts = df["Grade"].value_counts().reindex(GRADE_ORDER, fill_value=0)
    counts = counts[counts > 0]  # hide empty grades in the pie
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.pie(
        counts.values,
        labels=counts.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=[GRADE_COLORS[g] for g in counts.index],
        wedgeprops={"edgecolor": "white"},
    )
    ax.set_title("Grade Distribution")
    fig.tight_layout()
    return fig


def chart_subject_average(df):
    averages = df[SUBJECTS].mean().round(2)
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(averages.index, averages.values, color=sns.color_palette("viridis", len(SUBJECTS)))
    for bar, v in zip(bars, averages.values):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.5, f"{v:.1f}", ha="center", fontweight="bold")
    ax.set_ylim(0, 100)
    ax.set_title("Subject-wise Class Average")
    ax.set_xlabel("Subject")
    ax.set_ylabel("Average Marks")
    fig.tight_layout()
    return fig


def chart_percentage_hist(df):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(df["Percentage"], bins=10, color="#5c6bc0", edgecolor="white")
    ax.axvline(df["Percentage"].mean(), color="red", linestyle="--",
               label=f"Mean = {df['Percentage'].mean():.1f}%")
    ax.set_title("Distribution of Student Percentages")
    ax.set_xlabel("Percentage")
    ax.set_ylabel("Number of Students")
    ax.legend()
    fig.tight_layout()
    return fig


def chart_top5(df):
    top5 = df.nlargest(5, "Percentage").sort_values("Percentage")
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.barh(top5["Name"], top5["Percentage"], color=sns.color_palette("crest", len(top5)))
    for i, v in enumerate(top5["Percentage"]):
        ax.text(v + 0.3, i, f"{v:.1f}%", va="center")
    ax.set_xlim(0, 105)
    ax.set_title("Top 5 Students by Percentage")
    ax.set_xlabel("Percentage")
    ax.set_ylabel("Student")
    fig.tight_layout()
    return fig


def chart_student_vs_class(student, class_avg):
    """Compare one student's marks with the class average, subject by subject."""
    x = range(len(SUBJECTS))
    width = 0.38
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar([i - width / 2 for i in x], [student[s] for s in SUBJECTS],
           width, label=student["Name"], color="#5c6bc0")
    ax.bar([i + width / 2 for i in x], [class_avg[s] for s in SUBJECTS],
           width, label="Class Average", color="#bdbdbd")
    ax.set_xticks(list(x))
    ax.set_xticklabels(SUBJECTS)
    ax.set_ylim(0, 105)
    ax.set_title(f"{student['Name']} vs Class Average")
    ax.set_xlabel("Subject")
    ax.set_ylabel("Marks")
    ax.legend()
    fig.tight_layout()
    return fig


def chart_correlation(df):
    """Heatmap showing how subject marks relate to each other."""
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.heatmap(df[SUBJECTS].corr(), annot=True, fmt=".2f", cmap="coolwarm",
                vmin=-1, vmax=1, ax=ax)
    ax.set_title("Correlation Between Subjects")
    fig.tight_layout()
    return fig


def show_figure(fig):
    """Display a Matplotlib figure in Streamlit and free its memory."""
    st.pyplot(fig)
    plt.close(fig)


# ------------------------------------------------------------------
# Page layout
# ------------------------------------------------------------------
st.set_page_config(page_title="Student Performance Analysis", page_icon="🎓", layout="wide")

st.title("🎓 Student Performance Analysis")
st.write(
    "This dashboard analyses student marks in five subjects. It calculates total marks, "
    "percentage and grade, and shows class statistics with charts generated live from the data."
)

# ---- Sidebar: choose data source ----
st.sidebar.header("Data Source")
uploaded = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])
st.sidebar.caption("Required columns: " + ", ".join(REQUIRED_COLUMNS))

if uploaded is not None:
    source = uploaded
    st.sidebar.success("Using uploaded file.")
elif os.path.exists("students.csv"):
    source = "students.csv"
    st.sidebar.info("Using default file: students.csv")
else:
    st.error("students.csv not found. Run `python generate_data.py` first or upload a CSV.")
    st.stop()

# ---- Load data ----
try:
    results, warning_messages = load_and_process(source)
except Exception as err:
    st.error(f"Could not process the data: {err}")
    st.stop()

for msg in warning_messages:
    st.warning(msg)

# ---- Metric cards ----
st.header("Key Metrics")
top = results.loc[results["Total"].idxmax()]
low = results.loc[results["Total"].idxmin()]
pass_pct = (results["Percentage"] >= PASS_PERCENTAGE).mean() * 100

c1, c2, c3, c4 = st.columns(4)
c1.metric("Class Average", f"{results['Percentage'].mean():.2f}%",
          f"{results['Total'].mean():.1f} / {MAX_TOTAL}", delta_color="off")
c2.metric("Highest Scorer", top["Name"], f"{top['Total']:.0f} marks ({top['Percentage']:.2f}%)", delta_color="off")
c3.metric("Lowest Scorer", low["Name"], f"{low['Total']:.0f} marks ({low['Percentage']:.2f}%)", delta_color="off")
c4.metric("Pass Percentage", f"{pass_pct:.2f}%", f"{len(results)} students", delta_color="off")

# ---- Result table ----
st.header("Result Table")
st.dataframe(results, width="stretch", hide_index=True)

st.download_button(
    label="⬇️ Download results.csv",
    data=results.to_csv(index=False).encode("utf-8"),
    file_name="results.csv",
    mime="text/csv",
)

# ---- Subject-wise statistics ----
st.header("Subject-wise Statistics")
subject_stats = pd.DataFrame({
    "Highest": results[SUBJECTS].max(),
    "Lowest": results[SUBJECTS].min(),
    "Average": results[SUBJECTS].mean().round(2),
})
st.dataframe(subject_stats, width="stretch")

# ---- Charts (generated live) ----
st.header("Charts")
col_a, col_b = st.columns(2)
with col_a:
    show_figure(chart_grade_bar(results))
with col_b:
    show_figure(chart_grade_pie(results))

col_c, col_d = st.columns(2)
with col_c:
    show_figure(chart_subject_average(results))
with col_d:
    show_figure(chart_percentage_hist(results))

col_e, _ = st.columns(2)
with col_e:
    show_figure(chart_top5(results))

# ---- Extra insights ----
st.header("More Insights")
left, right = st.columns(2)
with left:
    st.subheader("Subject Toppers")
    toppers = pd.DataFrame({
        "Topper": [results.loc[results[sub].idxmax(), "Name"] for sub in SUBJECTS],
        "Marks": [results[sub].max() for sub in SUBJECTS],
    }, index=SUBJECTS)
    st.dataframe(toppers, width="stretch")

    st.subheader("Students Who Failed (below 50%)")
    failed = results[results["Percentage"] < PASS_PERCENTAGE]
    if failed.empty:
        st.success("No student failed.")
    else:
        st.dataframe(failed[["Student_ID", "Name", "Total", "Percentage", "Grade"]],
                     width="stretch", hide_index=True)
with right:
    show_figure(chart_correlation(results))

# ---- Student profile (search) ----
st.header("Student Profile")
query = st.text_input("Search student by name (or part of it)")
if query.strip():
    found = results[results["Name"].str.contains(query.strip(), case=False, na=False)]
    if found.empty:
        st.info("No student found with that name.")
    else:
        # If several names match, let the user pick one
        chosen = st.selectbox("Select student", found["Name"].tolist()) if len(found) > 1 else found["Name"].iloc[0]
        student = results[results["Name"] == chosen].iloc[0]
        class_avg = results[SUBJECTS].mean()

        # Rank 1 = highest total marks
        rank = int(results["Total"].rank(ascending=False, method="min")[student.name])
        strongest = student[SUBJECTS].astype(float).idxmax()
        weakest = student[SUBJECTS].astype(float).idxmin()

        p1, p2, p3, p4 = st.columns(4)
        p1.metric("Rank", f"{rank} / {len(results)}")
        p2.metric("Total", f"{student['Total']:.0f} / {MAX_TOTAL}")
        p3.metric("Percentage", f"{student['Percentage']:.2f}%")
        p4.metric("Grade", student["Grade"])

        status = "PASS" if student["Percentage"] >= PASS_PERCENTAGE else "FAIL"
        st.write(f"**Result:** {status} | **Strongest subject:** {strongest} "
                 f"({student[strongest]:.0f}) | **Weakest subject:** {weakest} ({student[weakest]:.0f})")

        # Subject-wise comparison table
        compare = pd.DataFrame({
            "Marks": [student[s] for s in SUBJECTS],
            "Class Average": [round(class_avg[s], 2) for s in SUBJECTS],
        }, index=SUBJECTS)
        compare["Difference"] = (compare["Marks"] - compare["Class Average"]).round(2)

        t_col, c_col = st.columns(2)
        with t_col:
            st.dataframe(compare, width="stretch")
        with c_col:
            show_figure(chart_student_vs_class(student, class_avg))
