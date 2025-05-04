import streamlit as st
import boto3
import pandas as pd
from datetime import datetime
from botocore.exceptions import ClientError
import io

# App Title
st.title("DA Workflow Check-In Portal")

# Inputs
da_name = st.text_input("Enter your name:")
workflow = st.selectbox("Select your current workflow:", [
    "Binary Preference", "MIL Workflow", "Sensitive Content RAI", "Transcription Workflow"
])

# AWS Credentials from .streamlit/secrets.toml
s3 = boto3.client(
    "s3",
    aws_access_key_id=st.secrets["aws"]["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=st.secrets["aws"]["AWS_SECRET_ACCESS_KEY"],
)

bucket_name = st.secrets["aws"]["S3_BUCKET"]
object_key = "logs/final_clean_checkin_log.csv"

if st.button("Check In"):
    try:
        # Try to get existing file
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        existing_data = response['Body'].read().decode('utf-8')
        df = pd.read_csv(io.StringIO(existing_data))
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            # File doesn't exist, create new DataFrame
            df = pd.DataFrame(columns=["DA Name", "Workflow", "Timestamp"])
        else:
            st.error(f" AWS GetObject Error: {e}")
            raise e

    # Append new check-in
    new_entry = pd.DataFrame({
        "DA Name": [da_name],
        "Workflow": [workflow],
        "Timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    })
    df = pd.concat([df, new_entry], ignore_index=True)

    # Convert back to CSV and upload
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)

    try:
        s3.put_object(
            Bucket=bucket_name,
            Key=object_key,
            Body=csv_buffer.getvalue()
        )
        st.success(" Workflow Check-In Recorded!")
    except Exception as e:
        st.error(f" Upload to S3 Failed: {e}")
