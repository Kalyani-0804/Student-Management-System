# 📊 Student Performance Analysis

A beginner-friendly **Python mini project** that analyses student marks in five subjects using basic data science techniques and displays results through an interactive Streamlit dashboard.

> **Course**: MCA | **Tools**: Python, Pandas, Matplotlib, Seaborn, Streamlit

---

## 🎯 Project Goal

Analyze marks of 40 students in **Maths, Science, English, History, and Computer** to:
- Calculate total marks, percentages, and assign letter grades
- Identify class toppers and subject-wise performance
- Visualize results using charts and an interactive dashboard

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Data Generation** | Creates a reproducible dataset of 40 students with realistic marks |
| **Data Validation** | Handles missing values and clips out-of-range marks |
| **Grade Assignment** | Automatic grading: A+, A, B, C, D, F |
| **Class Statistics** | Average, highest/lowest scorer, pass percentage |
| **Subject Analysis** | Per-subject highest, lowest, and average marks |
| **6 Visualizations** | Bar charts, pie chart, histogram, and box plot |
| **Streamlit Dashboard** | Interactive web app with search, download, and upload |
| **CSV Export** | Download the enriched results as `results.csv` |

---

## 📁 Project Structure

```
student-performance-analysis/
├── app.py                # Streamlit dashboard
├── analysis.py           # Core analysis logic & chart generation
├── generate_data.py      # Script to create students.csv
├── students.csv          # Input dataset (40 students)
├── results.csv           # Output with Total, Percentage, Grade
├── charts/               # Saved chart images (PNG)
│   ├── grade_bar_chart.png
│   ├── grade_pie_chart.png
│   ├── subject_average_chart.png
│   ├── percentage_histogram.png
│   ├── top5_students_chart.png
│   └── subject_box_plot.png
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

---

## 🚀 Setup & Run (Windows PowerShell)

### Prerequisites
- **Python 3.9+** installed and added to PATH
- **pip** (comes with Python)

### Step-by-step

```powershell
# 1. Navigate to the project folder
cd d:\CSR_project\student-performance-analysis

# 2. Create a virtual environment
python -m venv venv

# 3. Activate the virtual environment
.\venv\Scripts\Activate

# 4. Install required packages
pip install -r requirements.txt

# 5. Generate the student dataset
python generate_data.py

# 6. Run the analysis (prints stats to console + saves results.csv + generates charts)
python analysis.py

# 7. Launch the Streamlit dashboard
streamlit run app.py
```

The dashboard will open automatically in your default browser at `http://localhost:8501`.

---

## 📊 Grade Scale

| Percentage | Grade |
|------------|-------|
| 90% and above | A+ |
| 80% – 89.99% | A |
| 70% – 79.99% | B |
| 60% – 69.99% | C |
| 50% – 59.99% | D |
| Below 50% | F (Fail) |

---

## 📸 Sample Screenshots

> Screenshots will be added after the first run.

| Dashboard Overview | Charts |
|---|---|
| *(screenshot)* | *(screenshot)* |

---

## 🔧 How It Works

1. **`generate_data.py`** creates `students.csv` with 40 students and random marks (seed = 42 for reproducibility).
2. **`analysis.py`** loads the CSV, validates data, computes metrics (Total, Percentage, Grade), calculates statistics, and generates six chart images in `charts/`.
3. **`app.py`** provides an interactive Streamlit dashboard that displays all results, charts, metric cards, student search, and a CSV download button.

---

## 📝 Notes

- The random seed is fixed at **42**, so `generate_data.py` always produces the same dataset.
- Marks outside 0–100 are automatically clipped; missing values are filled with 0.
- You can upload your own CSV via the sidebar (must have the same column names).

---

## 📄 License

This project is created for educational purposes as part of an MCA course assignment.

---

*Built with ❤️ using Python, Pandas, Matplotlib, Seaborn & Streamlit*
