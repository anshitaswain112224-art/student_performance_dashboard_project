"""
Student Performance Analysis Dashboard
--------------------------------------
Built from the analysis in student_performance_anshita(2).ipynb.

Expected input:
  - student-mat.csv and student-por.csv in the same folder as app.py
    OR upload one/two CSV files from the dashboard.

Run:
  pip install -r requirements.txt
  python app.py
  Open http://127.0.0.1:8050 in your browser.
"""

from pathlib import Path
import base64
import io

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State, dash_table

APP_DIR = Path(__file__).resolve().parent
GRADE_ORDER = ["Poor", "Fair", "Excellent"]
GRADE_COLORS = {"Poor": "#E07A5F", "Fair": "#F2CC8F", "Excellent": "#81B29A"}

# Column names used in the uploaded notebook after its rename step.
NOTEBOOK_COLUMNS = [
    "school", "sex", "age", "address", "fam_size", "parents_status",
    "mother_edu", "father_edu", "mother_job", "father_job", "reason",
    "guardian", "travel_time", "study_time", "failures", "school_support",
    "fam_support", "paid_courses", "activities", "nursery", "higher",
    "internet", "romantic", "fam_rel", "free_time", "go_out",
    "weekday_alc", "weekend_alc", "health", "absences", "G1", "G2",
    "final_grade"
]

# Original UCI Student Performance column names, before the notebook rename.
ORIGINAL_COLUMNS = [
    "school", "sex", "age", "address", "famsize", "Pstatus", "Medu", "Fedu",
    "Mjob", "Fjob", "reason", "guardian", "traveltime", "studytime",
    "failures", "schoolsup", "famsup", "paid", "activities", "nursery",
    "higher", "internet", "romantic", "famrel", "freetime", "goout",
    "Dalc", "Walc", "health", "absences", "G1", "G2", "G3"
]

RENAME_MAP = dict(zip(ORIGINAL_COLUMNS, NOTEBOOK_COLUMNS))


def prepare_data(df):
    """Apply the notebook's column naming and grade-category logic safely."""
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    if set(ORIGINAL_COLUMNS).issubset(df.columns):
        df = df.rename(columns=RENAME_MAP)

    # Accept files that already use the notebook's renamed columns.
    if "final_grade" not in df.columns and "G3" in df.columns:
        df = df.rename(columns={"G3": "final_grade"})

    required = {"school", "sex", "age", "final_grade"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            "CSV is missing required columns: " + ", ".join(sorted(missing))
            + ". Please upload the Student Performance dataset "
              "(student-mat.csv / student-por.csv) or a combined CSV."
        )

    df["final_grade"] = pd.to_numeric(df["final_grade"], errors="coerce")
    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    df = df.dropna(subset=["final_grade", "age"]).copy()

    # Match the notebook: <=11 Poor, 12-15 Fair, >15 Excellent.
    df["remarks"] = pd.cut(
        df["final_grade"],
        bins=[float("-inf"), 11, 15, float("inf")],
        labels=GRADE_ORDER,
        right=True
    ).astype("object")

    numeric_cols = [
        "age", "mother_edu", "father_edu", "travel_time", "study_time",
        "failures", "fam_rel", "free_time", "go_out", "weekday_alc",
        "weekend_alc", "health", "absences", "G1", "G2", "final_grade"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def load_local_data():
    """Load the two source CSV files used in the notebook, if available."""
    mat_path = APP_DIR / "student-mat.csv"
    por_path = APP_DIR / "student-por.csv"
    frames = []
    for path in (mat_path, por_path):
        if path.exists():
            frames.append(pd.read_csv(path, sep=";"))
    if frames:
        combined = pd.concat(frames, ignore_index=True)
        combined = combined.drop_duplicates(keep="first")
        return prepare_data(combined), "Loaded local student-mat.csv / student-por.csv"
    return None, "Upload student-mat.csv and/or student-por.csv to begin."


def decode_upload(contents, filename):
    """Decode a Dash upload and parse a semicolon- or comma-separated CSV."""
    content_type, content_string = contents.split(",", 1)
    decoded = base64.b64decode(content_string)
    text = decoded.decode("utf-8-sig", errors="replace")
    # The original UCI files use semicolons; infer the delimiter.
    delimiter = ";" if text.splitlines() and text.splitlines()[0].count(";") > text.splitlines()[0].count(",") else ","
    return pd.read_csv(io.StringIO(text), sep=delimiter)


def card(title, value_id, subtitle=None):
    return html.Div(
        className="kpi-card",
        children=[
            html.Div(title, className="kpi-title"),
            html.Div(id=value_id, className="kpi-value"),
            html.Div(subtitle or "", className="kpi-subtitle"),
        ],
    )


initial_df, initial_status = load_local_data()
if initial_df is not None:
    INITIAL_DATA = initial_df.to_json(date_format="iso", orient="split")
else:
    INITIAL_DATA = None

app = Dash(__name__)
app.title = "Student Performance Dashboard"

app.layout = html.Div(
    className="page",
    children=[
        html.Header(
            className="hero",
            children=[
                html.Div("ACADEMIC PERFORMANCE • DATA ANALYSIS", className="eyebrow"),
                html.H1("Student Performance Dashboard"),
                html.P(
                    "Explore final grades and the factors examined in the Jupyter Notebook. "
                    "Use the filters to interact with every chart."
                ),
            ],
        ),
        html.Div(
            className="upload-panel",
            children=[
                html.Div(
                    [
                        html.H3("Load your dataset"),
                        html.P(
                            "Place student-mat.csv and student-por.csv beside app.py, "
                            "or upload either/both files here. You can also upload one "
                            "combined CSV."
                        ),
                    ]
                ),
                dcc.Upload(
                    id="upload-data",
                    children=html.Div(["Drag and drop CSV files or ", html.A("browse")]),
                    multiple=True,
                    className="upload-box",
                ),
                html.Div(initial_status, id="upload-status", className="status"),
            ],
        ),
        dcc.Store(id="dataset-store", data=INITIAL_DATA),
        html.Div(
            className="filters",
            children=[
                html.Div([html.Label("School"), dcc.Dropdown(id="school-filter", multi=True, placeholder="All schools")]),
                html.Div([html.Label("Gender"), dcc.Dropdown(id="sex-filter", multi=True, placeholder="All genders")]),
                html.Div([html.Label("Residence"), dcc.Dropdown(id="address-filter", multi=True, placeholder="All residences")]),
                html.Div([html.Label("Grade category"), dcc.Dropdown(
                    id="grade-filter", options=[{"label": x, "value": x} for x in GRADE_ORDER],
                    multi=True, placeholder="All grade categories"
                )]),
            ],
        ),
        html.Div(
            className="kpi-grid",
            children=[
                card("Students", "kpi-students"),
                card("Average final grade", "kpi-average", "Out of 20"),
                card("Excellent performers", "kpi-excellent"),
                card("Average absences", "kpi-absences"),
            ],
        ),
        html.Div(
            className="chart-grid",
            children=[
                html.Section([html.H3("Final grade distribution"), dcc.Graph(id="grade-distribution")], className="chart-card"),
                html.Section([html.H3("Performance by school"), dcc.Graph(id="school-performance")], className="chart-card"),
                html.Section([html.H3("Performance by gender"), dcc.Graph(id="gender-performance")], className="chart-card"),
                html.Section([html.H3("Study time and final grade"), dcc.Graph(id="study-performance")], className="chart-card"),
                html.Section([html.H3("Past class failures and final grade"), dcc.Graph(id="failure-performance")], className="chart-card"),
                html.Section([html.H3("Travel time and final grade"), dcc.Graph(id="travel-performance")], className="chart-card"),
                html.Section([html.H3("Parental education and final grade"), dcc.Graph(id="parent-education")], className="chart-card"),
                html.Section([html.H3("Internet access and final grade"), dcc.Graph(id="internet-performance")], className="chart-card"),
                html.Section([html.H3("Correlation heatmap"), dcc.Graph(id="correlation-heatmap")], className="chart-card wide"),
            ],
        ),
        html.Section(
            className="data-panel",
            children=[
                html.H3("Filtered student records"),
                html.P("A preview of the records after applying the filters."),
                dash_table.DataTable(
                    id="records-table",
                    page_size=10,
                    sort_action="native",
                    filter_action="native",
                    style_table={"overflowX": "auto"},
                    style_cell={"padding": "9px", "fontFamily": "Arial", "fontSize": 12, "textAlign": "left"},
                    style_header={"fontWeight": "bold", "backgroundColor": "#edf1f7"},
                ),
            ],
        ),
        html.Footer("Built with Python, Pandas, Plotly and Dash • Based on the uploaded Jupyter Notebook"),
    ],
)


@app.callback(
    Output("dataset-store", "data"),
    Output("upload-status", "children"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    prevent_initial_call=True,
)
def update_upload(contents, filenames):
    if not contents:
        return INITIAL_DATA, initial_status
    try:
        frames = [decode_upload(c, n) for c, n in zip(contents, filenames)]
        df = pd.concat(frames, ignore_index=True).drop_duplicates(keep="first")
        df = prepare_data(df)
        return df.to_json(date_format="iso", orient="split"), f"Loaded {len(df):,} student records from {', '.join(filenames)}."
    except Exception as exc:
        return INITIAL_DATA, f"Could not load file: {exc}"


@app.callback(
    Output("school-filter", "options"),
    Output("sex-filter", "options"),
    Output("address-filter", "options"),
    Input("dataset-store", "data"),
)
def populate_filters(data):
    if not data:
        return [], [], []
    df = pd.read_json(io.StringIO(data), orient="split")
    def options(col):
        if col not in df:
            return []
        return [{"label": str(v), "value": str(v)} for v in sorted(df[col].dropna().astype(str).unique())]
    return options("school"), options("sex"), options("address")


@app.callback(
    Output("kpi-students", "children"),
    Output("kpi-average", "children"),
    Output("kpi-excellent", "children"),
    Output("kpi-absences", "children"),
    Output("grade-distribution", "figure"),
    Output("school-performance", "figure"),
    Output("gender-performance", "figure"),
    Output("study-performance", "figure"),
    Output("failure-performance", "figure"),
    Output("travel-performance", "figure"),
    Output("parent-education", "figure"),
    Output("internet-performance", "figure"),
    Output("correlation-heatmap", "figure"),
    Output("records-table", "data"),
    Output("records-table", "columns"),
    Input("dataset-store", "data"),
    Input("school-filter", "value"),
    Input("sex-filter", "value"),
    Input("address-filter", "value"),
    Input("grade-filter", "value"),
)
def update_dashboard(data, schools, sexes, addresses, grades):
    empty = go.Figure().update_layout(template="plotly_white", annotations=[dict(text="Upload a dataset to view this chart", showarrow=False, x=0.5, y=0.5, xref="paper", yref="paper")])
    if not data:
        return ("—", "—", "—", "—", *([empty] * 9), [], [])

    df = pd.read_json(io.StringIO(data), orient="split")
    filtered = df.copy()
    for col, values in [("school", schools), ("sex", sexes), ("address", addresses), ("remarks", grades)]:
        if values and col in filtered:
            filtered = filtered[filtered[col].astype(str).isin([str(v) for v in values])]

    if filtered.empty:
        return ("0", "—", "0%", "—", *([empty] * 9), [], [])

    n = len(filtered)
    avg = filtered["final_grade"].mean()
    excellent = (filtered["remarks"] == "Excellent").mean() * 100
    avg_abs = filtered["absences"].mean() if "absences" in filtered else float("nan")

    grade_counts = filtered["remarks"].value_counts().reindex(GRADE_ORDER, fill_value=0).reset_index()
    grade_counts.columns = ["Grade category", "Students"]
    fig_grade = px.pie(grade_counts, names="Grade category", values="Students", hole=0.58,
                       color="Grade category", color_discrete_map=GRADE_COLORS)
    fig_grade.update_layout(template="plotly_white", legend_title_text="Grade category")

    if "school" in filtered:
        school_tab = filtered.groupby(["school", "remarks"], observed=False).size().reset_index(name="Students")
        school_tab["Percentage"] = school_tab["Students"] / school_tab.groupby("school")["Students"].transform("sum") * 100
        fig_school = px.bar(school_tab, x="school", y="Percentage", color="remarks", barmode="stack",
                            category_orders={"remarks": GRADE_ORDER}, color_discrete_map=GRADE_COLORS,
                            labels={"school": "School", "Percentage": "Students (%)", "remarks": "Grade category"})
    else:
        fig_school = empty

    if "sex" in filtered:
        gender_tab = filtered.groupby(["sex", "remarks"], observed=False).size().reset_index(name="Students")
        gender_tab["Percentage"] = gender_tab["Students"] / gender_tab.groupby("sex")["Students"].transform("sum") * 100
        fig_gender = px.bar(gender_tab, x="sex", y="Percentage", color="remarks", barmode="stack",
                            category_orders={"remarks": GRADE_ORDER}, color_discrete_map=GRADE_COLORS,
                            labels={"sex": "Gender", "Percentage": "Students (%)", "remarks": "Grade category"})
    else:
        fig_gender = empty

    def grouped_category(col, title, xlabel):
        if col not in filtered:
            return empty
        temp = filtered.groupby([col, "remarks"], observed=False).size().reset_index(name="Students")
        temp["Percentage"] = temp["Students"] / temp.groupby(col)["Students"].transform("sum") * 100
        fig = px.bar(temp, x=col, y="Percentage", color="remarks", barmode="stack",
                     category_orders={"remarks": GRADE_ORDER}, color_discrete_map=GRADE_COLORS,
                     labels={col: xlabel, "Percentage": "Students (%)", "remarks": "Grade category"})
        fig.update_layout(template="plotly_white")
        return fig

    fig_study = grouped_category("study_time", "Study time", "Study time category")
    fig_fail = grouped_category("failures", "Past failures", "Number of past failures")
    fig_travel = grouped_category("travel_time", "Travel time", "Travel time category")

    parent_cols = [c for c in ["mother_edu", "father_edu"] if c in filtered]
    if parent_cols:
        melted = filtered.melt(id_vars=["final_grade"], value_vars=parent_cols, var_name="Parent", value_name="Education level")
        fig_parent = px.box(melted, x="Education level", y="final_grade", color="Parent", points="outliers",
                            labels={"final_grade": "Final grade", "Parent": "Parent"})
        fig_parent.update_layout(template="plotly_white")
    else:
        fig_parent = empty

    fig_internet = grouped_category("internet", "Internet access", "Internet access")
    numeric = filtered.select_dtypes(include="number")
    if len(numeric.columns) >= 2:
        corr = numeric.corr()
        fig_corr = px.imshow(corr, text_auto=".2f", aspect="auto", color_continuous_scale="RdBu_r",
                             zmin=-1, zmax=1, labels=dict(color="Correlation"))
        fig_corr.update_layout(template="plotly_white")
    else:
        fig_corr = empty

    for fig in [fig_grade, fig_school, fig_gender, fig_study, fig_fail, fig_travel, fig_parent, fig_internet, fig_corr]:
        fig.update_layout(template="plotly_white", margin=dict(l=35, r=20, t=35, b=35), font=dict(family="Arial", size=12))
    fig_grade.update_layout(margin=dict(l=20, r=20, t=30, b=20))

    display_cols = [c for c in ["school", "sex", "age", "address", "study_time", "failures", "absences", "G1", "G2", "final_grade", "remarks"] if c in filtered]
    table = filtered[display_cols].head(500).copy()
    table = table.where(pd.notna(table), None).to_dict("records")
    columns = [{"name": c.replace("_", " ").title(), "id": c} for c in display_cols]

    return (
        f"{n:,}",
        f"{avg:.2f} / 20",
        f"{excellent:.1f}%",
        f"{avg_abs:.2f}" if pd.notna(avg_abs) else "N/A",
        fig_grade, fig_school, fig_gender, fig_study, fig_fail, fig_travel,
        fig_parent, fig_internet, fig_corr, table, columns
    )


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8050)
