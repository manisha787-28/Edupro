# Learner Demographics and Course Enrollment Behavior Analysis — EduPro

Descriptive analytics project on EduPro's learner base (3,000 users) and course
enrollment behavior (10,000 transactions across 60 courses and 60 teachers).

## Folder structure

```
EduPro_Project/
├── data/                        Raw source files (as uploaded, untouched)
│   ├── EduPro_Online_Platform_xlsx_-_Users.csv
│   ├── EduPro_Online_Platform_xlsx_-_Courses.csv
│   ├── EduPro_Online_Platform_xlsx_-_Transactions.csv
│   └── EduPro_Online_Platform_xlsx_-_Teachers.csv
│
├── scripts/                     Analysis pipeline (run in order)
│   ├── 01_data_check.py         Data quality checks (nulls, duplicates, referential integrity)
│   ├── 02_build_master.py       Joins Transactions + Users + Courses + Teachers into one table
│   ├── 03_analysis.py           All KPIs and descriptive statistics
│   ├── 04_charts.py             Generates the 10 charts used in the report
│   ├── build_research_paper.js  Builds outputs/EduPro_Research_Paper.docx
│   └── build_exec_summary.js    Builds outputs/EduPro_Executive_Summary.docx
│
├── outputs/                     Deliverables
│   ├── EduPro_Research_Paper.docx        Full EDA, findings, KPIs, recommendations
│   ├── EduPro_Executive_Summary.docx     Condensed summary for stakeholders
│   ├── master_dataset.csv                Joined, analysis-ready dataset (10,000 rows)
│   ├── users_enriched.csv                Users with AgeBand column added
│   └── chart_*.png                       Source charts used in the documents
│
└── app/                          Streamlit dashboard
    ├── app.py                    Dashboard source
    └── requirements.txt          pip dependencies
```

## Running the dashboard

```bash
cd app
pip install -r requirements.txt
streamlit run app.py
```

The app reads directly from `../data/`, re-derives the same joins and age bands
used in the analysis, and lets you filter by age group, gender, course category,
and course level across four tabs: Demographic Overview, Enrollment Patterns,
Demographics × Preferences, and Learner Behavior.

## Key data notes

- All four source files are clean: **zero nulls, zero duplicate keys, complete
  referential integrity** (every UserID/CourseID/TeacherID in Transactions exists
  in its parent table).
- Learner age in this dataset actually ranges **15–35** (not the wider range a
  general population might have), so age bands were scoped accordingly:
  Under 18, 18–22, 23–27, 28–31, 32–35.
- Enrollment behavior is **bimodal**: most learners enroll in 1–4 courses, but a
  distinct power-user segment enrolls in 11–16 courses. The top 10% of learners
  account for 42.3% of all enrollments — this is the single most actionable
  finding in the analysis.

## Headline numbers

| Metric | Value |
|---|---|
| Registered learners | 3,000 |
| Total enrollments | 10,000 |
| Gender split | 50.8% F / 49.2% M |
| Median learner age | 25 |
| Avg. enrollments / learner | 3.33 (median 1) |
| Top 10% enrollment concentration | 42.3% |
| Free vs. paid enrollments | 64.0% / 36.0% |
| Top course category | Data Science (9.2%) |
