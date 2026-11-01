# Student Performance Interactive Dashboard

This dashboard converts the analysis in `student_performance_anshita(2).ipynb` into an interactive Plotly Dash web app.

## 1. Put the files together

Keep `app.py` in a folder with the original dataset CSV files:

- `student-mat.csv`
- `student-por.csv`

The original notebook reads these files using a semicolon (`;`) separator. The app detects this automatically.

If you do not have the CSV files beside `app.py`, start the app anyway and upload the CSV file(s) through the dashboard. You can upload both original files together or one combined CSV.

## 2. Install the libraries

Open Terminal in this folder and run:

```bash
python3 -m pip install -r requirements.txt
```

## 3. Run the dashboard

```bash
python3 app.py
```

Then open this address in your browser:

http://127.0.0.1:8050

Keep the Terminal window running while you use the dashboard. Press `Control + C` in Terminal to stop it.

## Dashboard contents

- KPI cards: student count, average final grade, excellent-grade share, average absences
- Final grade distribution
- Grade category comparisons by school and gender
- Study time, past failures and travel time comparisons
- Parental education vs final grade
- Internet access comparison
- Numeric correlation heatmap
- Filterable and sortable student-record preview

## Grade categories

The notebook's original thresholds are preserved:

- Poor: final grade <= 11
- Fair: final grade 12–15
- Excellent: final grade > 15

## Important note

The uploaded notebook contains analysis code but does not contain the raw `student-mat.csv` and `student-por.csv` data files. The app therefore loads those CSV files from the same folder if present, or lets you upload them in the app. It does not invent student records.
