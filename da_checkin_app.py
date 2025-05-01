import streamlit as st
import boto3
import pandas as pd
from datetime import datetime
import io

# Page setup
st.set_page_config(page_title="DA Workflow Check-In", layout="centered")
st.title("DA Workflow Check-In Portal")

# Input fields
da_name = st.text_input("Enter your name:")
workflow = st.selectbox("Select your current workflow:", [
    "Binary Preference", "MIL Workflow", "Sensitive Content", "Transcription", "Other"
])

# Set up S3 client from Streamlit secrets
s3 = boto3.client(
    "s3",
    aws_access_key_id=st.secrets["aws"]["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=st.secrets["aws"]["AWS_SECRET_ACCESS_KEY"]
)

bucket_name = st.secrets["aws"]["S3_BUCKET"]
object_key = "logs/final_clean_checkin_log.csv"  # Static file path for consistent access

# Upload logic
if st.button("Check In"):
    if da_name and workflow:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_entry = pd.DataFrame([[da_name, workflow, timestamp]], columns=["DA Name", "Workflow", "Timestamp"])

        try:
            # Try to fetch existing file from S3
            response = s3.get_object(Bucket=bucket_name, Key=object_key)
            existing_data = pd.read_csv(io.BytesIO(response['Body'].read()))
            combined_data = pd.concat([existing_data, new_entry], ignore_index=True)
        except s3.exceptions.NoSuchKey:
            # If file doesn't exist, create new one
            combined_data = new_entry

        # Save updated CSV back to S3
        csv_buffer = io.StringIO()
        combined_data.to_csv(csv_buffer, index=False)
        s3.put_object(Bucket=bucket_name, Key=object_key, Body=csv_buffer.getvalue())

        st.success(f" {da_name} checked in to '{workflow}' at {timestamp}")
    else:
        st.warning(" Please enter your name and select a workflow.")
