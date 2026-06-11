"""
FastAPI Video Frame Search - Test Script

This script tests the video frame extraction and similarity search functionality
of the FastAPI application.

Author: [Mohammed Faris Sait]
Date: June 2025

Usage:
    1. Start the FastAPI server: uvicorn main:app --reload
    2. Add test files: sample.mp4 and query1.png
    3. Run this script: python test_fastapi_video_app.py
"""

import requests
import time
import os

# FastAPI server endpoints
UPLOAD_VIDEO_URL = "http://127.0.0.1:8000/upload-video/"
QUERY_IMAGE_URL = "http://127.0.0.1:8000/query/"

# Test file paths - update these with your actual test files
VIDEO_PATH = "sample.mp4"  # Replace with your test video file
QUERY_IMAGE_PATH = "query1.png"  # Replace with your test image file


def upload_video():
    """
    Upload a video file to extract frames

    Returns:
        bool: True if upload successful, False otherwise
    """
    # Check if video file exists
    if not os.path.exists(VIDEO_PATH):
        print(f" Video file not found: {VIDEO_PATH}")
        return None

    # Upload video file
    with open(VIDEO_PATH, "rb") as video_file:
        files = {"file": (VIDEO_PATH, video_file, "video/mp4")}
        print(" Uploading video...")
        response = requests.post(UPLOAD_VIDEO_URL, files=files)

    # Display results
    print(" Video Upload Response:", response.status_code)
    print(response.json())

    return response.ok


def upload_query():
    """
    Upload a query image to search for similar frames
    """
    # Check if query image exists
    if not os.path.exists(QUERY_IMAGE_PATH):
        print(f"Query image not found: {QUERY_IMAGE_PATH}")
        return

    # Upload query image
    with open(QUERY_IMAGE_PATH, "rb") as img_file:
        files = {"file": (QUERY_IMAGE_PATH, img_file, "image/jpeg")}
        print("Uploading query image...")
        response = requests.post(QUERY_IMAGE_URL, files=files)

    # Display results
    print("Query Response:", response.status_code)
    print(response.json())


# Main test execution
if __name__ == "__main__":
    """
    Run the complete test workflow:
    1. Upload video and extract frames
    2. Wait for processing to complete
    3. Query for similar frames
    """
    print("Starting FastAPI Video Frame Search Test")
    print("=" * 50)

    # Test video upload
    if upload_video():
        print(" Waiting a few seconds before querying...")
        time.sleep(3)  # Allow time for frames to be processed and saved

        # Test similarity query
        upload_query()

        print("=" * 50)
        print(" Test completed successfully!")
    else:
        print(" Video upload failed - skipping query test")
        print(" Make sure the FastAPI server is running and test files exist")
