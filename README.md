# vMix License Key Processor

This Streamlit application processes vMix license keys and provides various data processing features. It uses Selenium to scrape data from the vMix website, and Streamlit for the user interface.

## Features

- Upload Excel files with registration keys
- Process registration keys to retrieve vMix license data
- Display processed data and join it with the uploaded Excel data
- Download results as CSV files
- Dockerized for easy deployment

## Requirements

- Docker
- Docker Compose (optional)

## Getting Started

### Clone the Repository

```sh
git clone https://github.com/izyumovkirill/vMixLicenseKeyProcessor.git 
```

Build the Docker Image
Build the Docker image for the application:


```sh
docker build -t streamlit-vmix-app .
```
### Run the Docker Container
Run the Docker container for the application:

```sh

docker run -p 8501:8501 streamlit-vmix-app
```
### Access the Application
Open your web browser and navigate to **http://localhost:8501** to access the application.

## Usage
**Upload your Excel file**:  
Use the **"Upload your Excel file"** button to upload an Excel file containing registration keys.
**Select a column**: Choose the column containing registration keys from the dropdown menu in the sidebar.
**Start Processing**: Click the **"Start Processing"** button to begin data processing.
**View Results:** The processed data and joined data will be displayed on the screen.
**Download Results**: Use the **"Download vMix data as CSV"** and "Download joined data as CSV" buttons to download the respective CSV files.
### Dockerfile Explanation
Base Image: Uses python:3.12-slim for a lightweight Python environment.  
System Dependencies: Installs necessary system packages, Google Chrome, and ChromeDriver.  
Python Dependencies: Installs Python packages listed in requirements.txt.  
Run Command: Starts the Streamlit application on port 8501.  
Requirements.txt
streamlit
pandas
selenium
beautifulsoup4
webdriver-manager
### Troubleshooting
IndexError: If you encounter an IndexError, ensure that the data in the Download column is formatted correctly.
