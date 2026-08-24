"""
EduPro Learner Demographics and Course Enrollment Behavior Dashboard
Run with: streamlit run app.py
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="EduPro Learner Analytics", layout="wide", page_icon="📊")

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

DATA_DIR = "../data/"

@st.cache_data
def load_data():
    users = pd.read_csv(DATA_DIR + "EduPro_Online_Platform_xlsx_-_Users.csv")
    courses = pd.read_csv(DATA_DIR + "EduPro_Online_Platform_xlsx_-_Courses.csv")
    trans = pd.read_csv(DATA_DIR + "EduPro_Online_Platform_xlsx_-_Transactions.csv")
    teachers = pd.read_csv(DATA_DIR + "EduPro_Online_Platform_xlsx_-_Teachers.csv")

    trans["TransactionDate"] = pd.to_datetime(trans["TransactionDate"], format="%d/%m/%Y")

    band_order = ["Under 18", "18-22", "23-27", "28-31", "32-35"]

    def age_band(age):
        if age < 18:
            return "Under 18"
        elif age <= 22:
            return "18-22"
        elif age <= 27:
            return "23-27"
        elif age <= 31:
            return "28-31"
        else:
            return "32-35"

    users["AgeBand"] = pd.Categorical(users["Age"].apply(age_band), categories=band_order, ordered=True)

    master = (
        trans.merge(users, on="UserID", how="left", validate="many_to_one")
        .merge(courses, on="CourseID", how="left", validate="many_to_one")
        .merge(teachers, on="TeacherID", how="left", validate="many_to_one", suffixes=("_Learner", "_Teacher"))
    )
    master["AgeBand"] = pd.Categorical(
        master["Age_Learner"].apply(age_band), categories=band_order, ordered=True
    )
    return users, courses, trans, teachers, master, band_order


users, courses, trans, teachers, master, band_order = load_data()

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------

st.sidebar.title("Filters")

age_sel = st.sidebar.multiselect("Age Group", band_order, default=band_order)
gender_sel = st.sidebar.multiselect(
    "Gender", sorted(master["Gender_Learner"].unique()), default=sorted(master["Gender_Learner"].unique())
)
category_sel = st.sidebar.multiselect(
    "Course Category", sorted(master["CourseCategory"].unique()), default=sorted(master["CourseCategory"].unique())
)
level_sel = st.sidebar.multiselect(
    "Course Level", ["Beginner", "Intermediate", "Advanced"], default=["Beginner", "Intermediate", "Advanced"]
)

filtered = master[
    master["AgeBand"].isin(age_sel)
    & master["Gender_Learner"].isin(gender_sel)
    & master["CourseCategory"].isin(category_sel)
    & master["CourseLevel"].isin(level_sel)
]

st.sidebar.markdown("---")
st.sidebar.caption(f"Showing {len(filtered):,} of {len(master):,} enrollments")

# ---------------------------------------------------------------------------
# Header + KPIs
# ---------------------------------------------------------------------------

st.title("📊 EduPro — Learner Demographics & Enrollment Behavior")
st.caption("Descriptive learner intelligence dashboard for course design, engagement, and outreach decisions.")

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("Total Enrollments", f"{len(filtered):,}")
k2.metric("Unique Learners", f"{filtered['UserID'].nunique():,}")
k3.metric(
    "Gender Split (F/M)",
    f"{(filtered['Gender_Learner']=='Female').mean()*100:.0f}% / {(filtered['Gender_Learner']=='Male').mean()*100:.0f}%"
    if len(filtered) else "—",
)
top_cat = filtered["CourseCategory"].value_counts().idxmax() if len(filtered) else "—"
k4.metric("Top Category", top_cat)
avg_courses = filtered.groupby("UserID").size().mean() if len(filtered) else 0
k5.metric("Avg Courses / Learner", f"{avg_courses:.2f}")

st.markdown("---")

if len(filtered) == 0:
    st.warning("No data matches the selected filters. Please broaden your selection.")
    st.stop()

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs(
    ["👥 Demographic Overview", "📈 Enrollment Patterns", "🧭 Demographics × Preferences", "🔍 Learner Behavior"]
)

# --- Tab 1: Demographic overview -------------------------------------------------
with tab1:
    c1, c2 = st.columns(2)

    with c1:
        age_counts = (
            filtered.drop_duplicates("UserID")["AgeBand"].value_counts().reindex(band_order).fillna(0)
        )
        fig = px.bar(
            x=age_counts.index.astype(str), y=age_counts.values,
            labels={"x": "Age Band", "y": "Learners"}, title="Learner Age Distribution",
            color_discrete_sequence=["#4C72B0"],
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        gender_counts = filtered.drop_duplicates("UserID")["Gender_Learner"].value_counts()
        fig = px.pie(
            names=gender_counts.index, values=gender_counts.values, title="Learner Gender Distribution",
            color_discrete_sequence=["#4C72B0", "#DD8452"], hole=0.4,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Age Band vs Gender")
    ct = pd.crosstab(filtered.drop_duplicates("UserID")["AgeBand"], filtered.drop_duplicates("UserID")["Gender_Learner"])
    fig = px.bar(ct, barmode="group", title="Learners by Age Band and Gender", labels={"value": "Learners", "AgeBand": "Age Band"})
    st.plotly_chart(fig, use_container_width=True)

# --- Tab 2: Enrollment patterns -------------------------------------------------
with tab2:
    c1, c2 = st.columns(2)

    with c1:
        cat_counts = filtered["CourseCategory"].value_counts().sort_values()
        fig = px.bar(
            x=cat_counts.values, y=cat_counts.index, orientation="h",
            labels={"x": "Enrollments", "y": "Category"}, title="Course Category Popularity",
            color_discrete_sequence=["#55A868"],
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        level_counts = filtered["CourseLevel"].value_counts().reindex(["Beginner", "Intermediate", "Advanced"]).fillna(0)
        fig = px.bar(
            x=level_counts.index, y=level_counts.values, title="Enrollments by Course Level",
            labels={"x": "Level", "y": "Enrollments"}, color=level_counts.index,
            color_discrete_map={"Beginner": "#55A868", "Intermediate": "#DD8452", "Advanced": "#C44E52"},
        )
        st.plotly_chart(fig, use_container_width=True)

    type_counts = filtered["CourseType"].value_counts()
    fig = px.pie(names=type_counts.index, values=type_counts.values, title="Free vs Paid Enrollments", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Monthly Enrollment Trend")
    monthly = filtered.copy()
    monthly["Month"] = monthly["TransactionDate"].dt.to_period("M").astype(str)
    trend = monthly.groupby("Month").size().reset_index(name="Enrollments")
    fig = px.line(trend, x="Month", y="Enrollments", markers=True, title="Enrollments Over Time")
    st.plotly_chart(fig, use_container_width=True)

# --- Tab 3: Demographics x preferences -------------------------------------------------
with tab3:
    st.subheader("Age Band vs Course Category (Heatmap)")
    ct = pd.crosstab(filtered["AgeBand"], filtered["CourseCategory"])
    fig = px.imshow(ct, text_auto=True, aspect="auto", color_continuous_scale="YlGnBu",
                     labels=dict(x="Course Category", y="Age Band", color="Enrollments"))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Course Level Preference by Gender")
    ct2 = pd.crosstab(filtered["Gender_Learner"], filtered["CourseLevel"], normalize="index")[
        [c for c in ["Beginner", "Intermediate", "Advanced"] if c in filtered["CourseLevel"].unique()]
    ] * 100
    fig = px.bar(ct2, barmode="stack", title="Course Level Preference by Gender (%)",
                 labels={"value": "% of Enrollments", "Gender_Learner": "Gender"},
                 color_discrete_map={"Beginner": "#55A868", "Intermediate": "#DD8452", "Advanced": "#C44E52"})
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Free vs Paid Preference by Course Level")
    rows = []
    for lvl in ["Beginner", "Intermediate", "Advanced"]:
        sub = filtered[filtered["CourseLevel"] == lvl]
        if len(sub) == 0:
            continue
        vc = sub["CourseType"].value_counts(normalize=True) * 100
        rows.append({"Level": lvl, "Free": vc.get("Free", 0), "Paid": vc.get("Paid", 0)})
    if rows:
        df_fp = pd.DataFrame(rows).set_index("Level")
        fig = px.bar(df_fp, barmode="group", title="Free vs Paid by Level (%)",
                     color_discrete_map={"Free": "#55A868", "Paid": "#C44E52"})
        st.plotly_chart(fig, use_container_width=True)

# --- Tab 4: Learner behavior -------------------------------------------------
with tab4:
    per_user = filtered.groupby("UserID").size()

    c1, c2, c3 = st.columns(3)
    c1.metric("Avg Courses / Learner", f"{per_user.mean():.2f}")
    c2.metric("Median Courses / Learner", f"{per_user.median():.0f}")
    c3.metric("Max Courses (single learner)", f"{per_user.max():.0f}")

    fig = px.histogram(per_user, nbins=int(per_user.max()), title="Distribution of Enrollments per Learner",
                        labels={"value": "Courses Enrolled", "count": "Learners"})
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    sorted_counts = per_user.sort_values(ascending=False)
    top10_n = max(1, int(len(sorted_counts) * 0.10))
    top10_share = sorted_counts.head(top10_n).sum() / sorted_counts.sum() * 100 if sorted_counts.sum() else 0
    st.info(
        f"The top 10% most active learners ({top10_n:,} of {len(sorted_counts):,}) account for "
        f"**{top10_share:.1f}%** of all enrollments in the current filter."
    )

    st.subheader("Explore Raw Enrollment Records")
    st.dataframe(
        filtered[
            ["TransactionID", "UserID", "Age_Learner", "Gender_Learner", "CourseName",
             "CourseCategory", "CourseLevel", "CourseType", "TransactionDate"]
        ].sort_values("TransactionDate", ascending=False),
        use_container_width=True,
        height=350,
    )

st.markdown("---")
st.caption("EduPro Learner Demographics and Course Enrollment Behavior Analysis — descriptive analytics only, no predictive or monetization modeling.")
