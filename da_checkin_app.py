import streamlit as st
import boto3
from datetime import datetime

# Set up the Streamlit app layout and title
st.set_page_config(page_title="DA Workflow Check-In", layout="centered")
st.title("DA Workflow Check-In Portal")

# Input fields for DA name and selected workflow
da_name = st.text_input("Enter your name:")
workflow = st.selectbox("Select your current workflow:", [
    "Binary Preference", "MIL Workflow", "Sensitive Content", "Transcription", "Other"
])

# Initialize S3 client from Streamlit secrets
s3 = boto3.client(
    "s3",
    aws_access_key_id=st.secrets["aws"]["AKIAQQ6R5IZLJDK2FTMF"],
    aws_secret_access_key=st.secrets["aws"]["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"]
)
bucket_name = st.secrets["aws"]["S3_BUCKET"]

# Button logic
if st.button("Check In"):
    if da_name and workflow:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        csv_line = f"{da_name},{workflow},{timestamp}\n"
        object_key = f"logs/{da_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        try:
            s3.put_object(Bucket=bucket_name, Key=object_key, Body=csv_line)
            st.success(f"{da_name} checked in to '{workflow}' at {timestamp}")
        except Exception as e:
            st.error(f"Error uploading to S3: {e}")
    else:
        st.warning("Please enter your name and select a workflow before submitting.")
