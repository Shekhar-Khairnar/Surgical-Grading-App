import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO


# Initialize global data list in session state
if 'data' not in st.session_state:
    st.session_state.data = []

# Dropdown options
procedures = ['GJ', 'PJ', 'HJ']
scores = [str(i) for i in range(1, 6)]  # Score values
osats_metrics = ['', 'Respect for tissue', 'Time and motion', 'Instrument handling',
                 'Knowledge of instruments', 'Use of assistance',
                 'Flow/forward progress', 'Knowledge of procedure']

# Initialize the session state for dynamic entry count with a default of 7 entries
if 'num_entries' not in st.session_state:
    st.session_state.num_entries = 7  # Start with 7 default entries

# Function to add a new entry by incrementing the session state
def add_entry():
    st.session_state.num_entries += 1

# Title of the app
st.title("Surgical Grading App")

# Procedure and grader information
st.subheader("Procedure Information")
cols = st.columns(4)  # Display Name, Date, Procedure, and Grader in a single row

with cols[0]:
    name = st.text_input("Medical student name", "")
with cols[1]:
    date = st.date_input("Date", datetime.now())
with cols[2]:
    procedure = st.selectbox("Procedure", procedures)
with cols[3]:
    grader = st.text_input("Grader Name", "")

# Time dropdown options (with an initial empty string)
hours = [""] + [f"{i:02}" for i in range(24)]
minutes_seconds = [""] + [f"{i:02}" for i in range(60)]

# Form for user input
st.subheader("Enter Time, Comments, OSATS Metric, and Remarks for Each Entry")

# Create the input fields dynamically based on the number of entries in the session state
dynamic_entries = []
for i in range(st.session_state.num_entries):
    with st.expander(f"Entry {i + 1}", expanded=(i == 0)):  # Expand only the first entry by default
        # Create columns for Hour, Minute, Second, Comment, OSATS Metric, and Remarks
        cols = st.columns([2, 4, 6, 4,1])  # Adjust column widths to fit everything on one line

        # Time input for hours, minutes, and seconds
        with cols[0]:
            hour = st.selectbox(f"Hour {i + 1}", hours, key=f'hour_{i}')
            minute = st.selectbox(f"Minute {i + 1}", minutes_seconds, key=f'minute_{i}')
            second = st.selectbox(f"Second {i + 1}", minutes_seconds, key=f'second_{i}')
            time_stamp = f"{hour}:{minute}:{second}" if hour and minute and second else ""

        # Comment input
        with cols[1]:
            comment = st.text_area(f"Comment {i + 1}", "", key=f'comment_{i}')

        # OSATS Metric input (keeping the empty option)
        with cols[2]:
            osats_metric = st.selectbox(f"OSATS Metric {i + 1}", osats_metrics, key=f"osats_{i}")

        # Remarks input
        with cols[3]:
            remarks = st.text_area(f"Remarks {i + 1}", "", key=f'remarks_{i}')

        # Append this entry (only non-empty entries)
        if time_stamp or comment.strip() or remarks.strip() or osats_metric.strip() != ' ':
            dynamic_entries.append((time_stamp, comment, osats_metric, remarks))

# Button to add new entries outside the form
st.button("+ Add more Entries", on_click=add_entry)

# Total Procedure Time and Errors
st.subheader("Summary")
st.subheader('Total Procedure Time')
cols = st.columns(3)  # Adjust Total Procedure Time and Total Errors in a single row

# Total Procedure Time
with cols[0]:
    total_hour = st.selectbox("Hour", hours, key='total_hour')
with cols[1]:
    total_minute = st.selectbox("Minute", minutes_seconds, key='total_minute')
with cols[2]:
    total_second = st.selectbox("Second", minutes_seconds, key='total_second')
total_time = f"{total_hour}:{total_minute}:{total_second}" if total_hour and total_minute and total_second else ""

st.subheader('Total Errors')
cols = st.columns(1)  # Adjust Total Procedure Time and Total Errors in a single row

# Total Errors
with cols[0]:
    total_errors = st.number_input("", min_value=0, step=1, value=0)

st.subheader("OSATS Scores")

# Collect OSATS Scores for only required OSATS metrics
osats_scores = {}
for metric in osats_metrics:
    if metric:
        osats_scores[metric] = st.selectbox(f"{metric} Score", scores, key=f"score_{metric}")

# Save Button to Save Data
if st.button("Save"):
    if not name or not grader:
        st.error("Please enter the Name and Grader information.")
    else:
        # Save the entry
        entry_data = {
            "Name": name,
            "Date": date.strftime('%Y-%m-%d'),  # Format date as string
            "Procedure": procedure,
            "Grader": grader,
            "Time_Entries": dynamic_entries,
            "Total_Time": total_time,
            "Total_Errors": total_errors,
            "OSATS_Scores": osats_scores
        }

        # Add entry to session data list
        st.session_state.data.append(entry_data)

        st.success("Entry saved successfully!")

# CSV Export Functionality
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# Export to CSV Button
if st.button("Export to download CSV file"):
    if not st.session_state.data:
        st.error("No data to export. Please save entries first.")
    else:
        # Convert the data into a DataFrame for export (format row-wise)
        rows = []

        # Add a general header row with Name, Date, Procedure, Grader
        rows.append(["Name", st.session_state.data[-1]['Name']])
        rows.append(["Date", st.session_state.data[-1]['Date']])
        rows.append(["Procedure", st.session_state.data[-1]['Procedure']])
        rows.append(["Grader", st.session_state.data[-1]['Grader']])

        # Add section for each entry (with numbered labels like Time 1, Comment 1, etc.)
        for idx, time_entry in enumerate(st.session_state.data[-1]['Time_Entries'], start=1):
            time_stamp, comment, osats_metric, remarks = time_entry
            rows.append([f"Time {idx}", time_stamp])
            rows.append([f"Comment {idx}", comment])
            rows.append([f"OSATS Metric {idx}", osats_metric])
            rows.append([f"Remarks {idx}", remarks])

        # Add total procedure time and total errors
        rows.append(["Total Procedure Time", st.session_state.data[-1]['Total_Time']])
        rows.append(["Total Errors", st.session_state.data[-1]['Total_Errors']])

        # Add OSATS Metrics and Scores at the bottom
        rows.append(["OSATS Metrics and Scores"])
        osats_total = 0
        for metric, score in st.session_state.data[-1]['OSATS_Scores'].items():
            if score.isdigit():
                osats_total += int(score)
            rows.append([metric, score])

        # Add total OSATS score after the metrics
        rows.append(["Total OSATS Score", osats_total])

        # Convert the rows into a DataFrame
        df = pd.DataFrame(rows)
        # Replace empty strings with NaN to properly drop empty rows
        df.replace("", pd.NA, inplace=True)

        # Drop any empty cells from the DataFrame before exporting
        df = df.dropna(axis=0, how='any')

        # Convert the DataFrame to CSV
        csv = convert_df_to_csv(df)

        # Generate a safe filename based on name, grader, and date
        name_safe = st.session_state.data[-1]['Name'].replace(" ", "_")
        grader_safe = st.session_state.data[-1]['Grader'].replace(" ", "_")
        date_safe = st.session_state.data[-1]['Date'].replace("-", "_")

        # Construct the filename
        csv_filename = f"{name_safe}_{grader_safe}_{date_safe}.csv"

        # Provide download button for CSV
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=csv_filename,  # Use the dynamic filename here
            mime='text/csv'
        )

