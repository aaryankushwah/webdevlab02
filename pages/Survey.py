# This creates the page for users to input data.
# The collected data should be appended to the 'data.csv' file.

import streamlit as st
import pandas as pd
import os  # For file checks

# PAGE CONFIGURATION
st.set_page_config(
    page_title="Survey",
    page_icon="📝",
)

# PAGE TITLE AND USER DIRECTIONS
st.title("Data Collection Survey 📝")
st.write("Log a longevity metric below to add it to the dataset (e.g., sleep hours, steps, protein).")

# Ensure CSV exists with headers
CSV_PATH = "data.csv"
COLUMNS = ["Category", "Value"]
if not os.path.exists(CSV_PATH) or os.path.getsize(CSV_PATH) == 0:
    pd.DataFrame(columns=COLUMNS).to_csv(CSV_PATH, index=False)

# DATA INPUT FORM
with st.form("survey_form"):
    st.caption("Tip: choose a metric or select 'Other' to type your own.")

    # Pre-populated longevity metrics (you can still type your own via 'Other')
    preset = st.selectbox(
        "Pick a longevity metric",
        [
            "Sleep (hours)",
            "Steps (count)",
            "Protein (grams)",
            "Water (oz)",
            "Exercise (minutes)",
            "Meditation (minutes)",
            "Screen Time (hours)",
            "HRV (ms)",
            "VO₂max",
            "Other",
        ],
    )

    # Maintain the original variable names to respect the skeleton, but map them to our UI
    # Category input (if "Other" is chosen, ask for a custom name)
    category_input = (
        st.text_input("Or enter a custom metric name (used if 'Other' selected):").strip()
        if preset == "Other"
        else preset
    )

    # Numeric value input
    value_input = st.number_input("Enter the value", min_value=0.0, step=0.1, format="%.2f")

    submitted = st.form_submit_button("Submit Data")

    if submitted:
        # Guardrails: require a non-empty category
        if isinstance(category_input, str):
            category_clean = category_input.strip()
        else:
            category_clean = str(category_input)

        if preset == "Other" and not category_clean:
            st.error("Please provide a name for your custom metric.")
        else:
            # Append to CSV (header only written if file is empty)
            new_row = pd.DataFrame([{"Category": category_clean, "Value": value_input}])
            write_header = os.path.getsize(CSV_PATH) == 0
            new_row.to_csv(CSV_PATH, mode="a", header=write_header, index=False)

            st.success("Your data has been submitted!")
            st.write(f"You entered: **Category:** {category_clean}, **Value:** {value_input:.2f}")

# DATA DISPLAY
st.divider()
st.header("Current Data in CSV")

if os.path.exists(CSV_PATH) and os.path.getsize(CSV_PATH) > 0:
    current_data_df = pd.read_csv(CSV_PATH)
    st.dataframe(current_data_df, use_container_width=True)
else:
    st.warning("The 'data.csv' file is empty or does not exist yet.")
