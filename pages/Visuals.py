# This creates the page for displaying data visualizations.
# It should read data from both 'data.csv' and 'data.json' to create graphs.

import streamlit as st
import pandas as pd
import json # The 'json' module is needed to work with JSON files.
import os   # The 'os' module helps with file system operations.

# PAGE CONFIGURATION
st.set_page_config(
    page_title="Visualizations",
    page_icon="📈",
)

# PAGE TITLE AND INFORMATION
st.title("Data Visualizations 📈")
st.write("This page displays graphs based on the collected data.")


# DATA LOADING
# A crucial step is to load the data from the files.
# It's important to add error handling to prevent the app from crashing if a file is empty or missing.

st.divider()
st.header("Load Data")

# TO DO:
# 1. Load the data from 'data.csv' into a pandas DataFrame.
#    - Use a 'try-except' block or 'os.path.exists' to handle cases where the file doesn't exist.
# 2. Load the data from 'data.json' into a Python dictionary.
#    - Use a 'try-except' block here as well.

# ---- CSV ----
if os.path.exists('data.csv') and os.path.getsize('data.csv') > 0:
    try:
        csv_df = pd.read_csv('data.csv')
        # normalize column names and coerce numeric values
        csv_df.columns = [c.strip().title() for c in csv_df.columns]
        if "Value" in csv_df.columns:
            csv_df["Value"] = pd.to_numeric(csv_df["Value"], errors="coerce")
        csv_df = csv_df.dropna(subset=["Category", "Value"])
    except Exception as e:
        st.error(f"Failed to read data.csv: {e}")
        csv_df = pd.DataFrame(columns=["Category", "Value"])
else:
    csv_df = pd.DataFrame(columns=["Category", "Value"])

# ---- JSON ----
json_title = "JSON Data"
json_df = pd.DataFrame(columns=["label", "value"])
if os.path.exists('data.json') and os.path.getsize('data.json') > 0:
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            jdata = json.load(f)
        json_title = jdata.get("chart_title", "JSON Data")
        points = jdata.get("data_points", [])
        json_df = pd.DataFrame(points)
        if not {"label", "value"}.issubset(json_df.columns):
            json_df = pd.DataFrame(columns=["label", "value"])
        else:
            json_df["value"] = pd.to_numeric(json_df["value"], errors="coerce")
            json_df = json_df.dropna(subset=["label", "value"])
    except Exception as e:
        st.error(f"Failed to read data.json: {e}")
        json_df = pd.DataFrame(columns=["label", "value"])

# quick status
c1, c2 = st.columns(2)  # NEW
with c1:
    st.metric("CSV Rows Loaded", len(csv_df))  # NEW
with c2:
    st.metric("JSON Points Loaded", len(json_df))  # NEW


# GRAPH CREATION
# The lab requires you to create 3 graphs: one static and two dynamic.
# You must use both the CSV and JSON data sources at least once.

st.divider()
st.header("Graphs")

# GRAPH 1: STATIC GRAPH
st.subheader("Graph 1: Static") # CHANGE THIS TO THE TITLE OF YOUR GRAPH
# TO DO:
# - Create a static graph (e.g., bar chart, line chart) using st.bar_chart() or st.line_chart().
# - Use data from either the CSV or JSON file.
# - Write a description explaining what the graph shows.

if not json_df.empty:
    static_bar = json_df.rename(columns={"label": "Label", "value": "Value"}).set_index("Label")[["Value"]]
    st.bar_chart(static_bar, use_container_width=True)
    st.write(f"**Description:** Static bar chart using your JSON dataset (**{json_title}**). Each bar is a factor (e.g., Sleep, Exercise) and its value.")
else:
    st.warning("No JSON data available yet for the static chart. Edit data.json to add labels and values.")


# GRAPH 2: DYNAMIC GRAPH
st.subheader("Graph 2: Dynamic") # CHANGE THIS TO THE TITLE OF YOUR GRAPH
# TODO:
# - Create a dynamic graph that changes based on user input.
# - Use at least one interactive widget (e.g., st.slider, st.selectbox, st.multiselect).
# - Use Streamlit's Session State (st.session_state) to manage the interaction.
# - Add a '#NEW' comment next to at least 3 new Streamlit functions you use in this lab.
# - Write a description explaining the graph and how to interact with it.

# Defaults for session state
if "selected_categories" not in st.session_state:
    st.session_state.selected_categories = []
if "chart_type" not in st.session_state:
    st.session_state.chart_type = "Line"
if "show_last_n" not in st.session_state:
    st.session_state.show_last_n = 0  # 0 = show all
if "use_cumulative" not in st.session_state:
    st.session_state.use_cumulative = False

# Controls
all_categories = sorted(csv_df["Category"].dropna().unique().tolist()) if not csv_df.empty else []
st.session_state.selected_categories = st.multiselect(  # NEW
    "Select categories from CSV to display",
    options=all_categories,
    default=st.session_state.selected_categories,
)

st.session_state.chart_type = st.radio(  # NEW
    "Chart type",
    ["Line", "Bar"],
    horizontal=True
)

st.session_state.show_last_n = st.number_input(  # NEW
    "Show only the last N entries per category (0 = all)",
    min_value=0, max_value=1000, value=int(st.session_state.show_last_n), step=1
)

st.session_state.use_cumulative = st.toggle(  # NEW
    "Show cumulative sum",
    value=bool(st.session_state.use_cumulative)
)

# Build wide table: x-axis = entry order per category
if csv_df.empty or not all_categories:
    st.warning("CSV has no data yet. Add entries on the Survey page.")
else:
    chosen = st.session_state.selected_categories or all_categories
    df = csv_df[csv_df["Category"].isin(chosen)].copy()
    # assign per-category sequence index
    df["Entry #"] = df.groupby("Category").cumcount() + 1

    # keep only the last N per category if requested
    N = int(st.session_state.show_last_n)
    if N > 0:
        df = df.groupby("Category", group_keys=False).tail(N)

    # rebuild the sequence index after trimming, so charts start at 1..N
    df["Entry #"] = df.groupby("Category").cumcount() + 1

    wide = df.pivot(index="Entry #", columns="Category", values="Value").sort_index()

    # cumulative sum (per series)
    if st.session_state.use_cumulative and not wide.empty:
        wide = wide.cumsum()

    if st.session_state.chart_type == "Line":
        st.line_chart(wide, use_container_width=True)
    else:
        st.bar_chart(wide, use_container_width=True)

    st.write("**How to use:** Pick one or more categories, choose Line or Bar, optionally limit to the last N points, and toggle cumulative sum.")
    with st.expander("View CSV data used in this chart"):  # NEW
        st.dataframe(wide, use_container_width=True)


# GRAPH 3: DYNAMIC GRAPH
st.subheader("Graph 3: Dynamic") # CHANGE THIS TO THE TITLE OF YOUR GRAPH
# TO DO:
# - Create another dynamic graph.
# - If you used CSV data for Graph 1 & 2, you MUST use JSON data here (or vice-versa).
# - This graph must also be interactive and use Session State.
# - Remember to add a description and use '#NEW' comments.

if json_df.empty:
    st.warning("No JSON data yet. Populate data.json to use this graph.")
else:
    jdf = json_df.rename(columns={"label": "Label", "value": "Value"})[["Label", "Value"]].copy()

    # Initialize JSON weights in session state
    if "json_weights" not in st.session_state:
        st.session_state.json_weights = {lbl: 1.0 for lbl in jdf["Label"].tolist()}

    st.write("Adjust weights for each JSON factor:")
    for lbl in jdf["Label"]:
        current = float(st.session_state.json_weights.get(lbl, 1.0))
        st.session_state.json_weights[lbl] = st.slider(  # NEW
            f"{lbl} weight",
            min_value=0.0, max_value=3.0, value=current, step=0.1
        )

    # Apply weights
    jdf["Weighted"] = jdf.apply(lambda r: r["Value"] * st.session_state.json_weights.get(r["Label"], 1.0), axis=1)

    normalize = st.toggle("Normalize to percentage", value=False)  # NEW
    plot_df = jdf.set_index("Label")[["Weighted"]].copy()
    if normalize:
        total = float(plot_df["Weighted"].sum())
        if total > 0:
            plot_df["Weighted"] = (plot_df["Weighted"] / total) * 100.0

    st.area_chart(plot_df, use_container_width=True)
    st.write("**Description:** Dynamic area chart using JSON data. Move the sliders to change factor weights; optionally normalize to percentages.")
