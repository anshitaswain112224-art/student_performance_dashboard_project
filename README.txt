
# Student Performance Interactive Dashboard

This project converts the analysis performed in `student_performance_anshita(2).ipynb` into an interactive web dashboard using Python, Plotly and Dash.

The dashboard allows users to explore student academic performance and understand patterns through interactive charts and visualizations.

## 1. Project Setup

Keep `app.py` in a folder with the original dataset CSV files:

- `student-mat.csv`
- `student-por.csv`

The original notebook reads these files using a semicolon (`;`) separator. The application detects this automatically.

If the CSV files are not available in the same folder, you can upload them directly through the dashboard.

You can upload both original files or one combined CSV file.

## 2. Install Required Libraries

Open Terminal in the project folder and run:

```bash
python3 -m pip install -r requirements.txt
```

## 3. Run the Dashboard

Execute the following command in Terminal:

```bash
python3 app.py
```

Open the following address in your web browser:

http://127.0.0.1:8050

Keep the Terminal window running while using the dashboard.

To stop the application, press `Control + C` in Terminal.

## 4. Dashboard Features

The interactive dashboard includes:

- **KPI Cards:** Total number of students, average final grade, percentage of excellent performers and average absences.
- **Final Grade Distribution:** Visual representation of Poor, Fair and Excellent grade categories.
- **School Comparison:** Comparison of academic performance across schools.
- **Gender Comparison:** Analysis of grade categories by gender.
- **Study Time Analysis:** Relationship between study time and academic performance.
- **Previous Failures:** Comparison of academic performance based on previous failures.
- **Travel Time Analysis:** Exploration of travel time and final grades.
- **Parental Education:** Comparison of parental education levels with students' grades.
- **Internet Access:** Analysis of academic performance based on internet availability.
- **Correlation Heatmap:** Visualization of relationships between numerical variables.
- **Student Records:** Interactive, sortable and filterable student data table.

## 5. Grade Categories

The dashboard follows the grade classification used in the original notebook:

| Grade Category | Final Grade |
|---|---|
| Poor | Less than or equal to 11 |
| Fair | 12–15 |
| Excellent | Greater than 15 |

## 6. Technologies Used

- Python
- Pandas
- NumPy
- Plotly
- Dash
- HTML and CSS

## 7. Dataset Information

The project uses the Student Performance dataset, containing information about students' academic results, personal backgrounds, family characteristics and study habits.

The uploaded Jupyter Notebook contains the analysis code but does not include the original CSV files (`student-mat.csv` and `student-por.csv`).

Therefore, the application loads the CSV files from the project folder when available or allows users to upload them through the dashboard.

No artificial student records are generated.

## 8. Project Objective

The main objective of this project is to transform the findings from data analysis into an interactive dashboard.

It provides an accessible way to explore student performance, identify patterns and understand relationships between academic results and different influencing factors.
