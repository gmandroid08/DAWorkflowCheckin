import streamlit as st
import boto3
from datetime import datetime

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

# Upload logic
if st.button("Check In"):
    if da_name and workflow:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Always include header row in each CSV
        header = "DA Name,Workflow,Timestamp\n"
        data_line = f"{da_name},{workflow},{timestamp}\n"
        log_data = header + data_line
        
        object_key = f"logs/{da_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        try:
            s3.put_object(Bucket=bucket_name, Key=object_key, Body=log_data)
            st.success(f"{da_name} checked in to '{workflow}' at {timestamp}")
        except Exception as e:
            st.error(f"Error uploading to S3: {e}")
    else:
        st.warning("Please enter your name and select a workflow.")
