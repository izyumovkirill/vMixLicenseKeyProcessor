import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from bs4 import BeautifulSoup

# Установка wide режима
st.set_page_config(layout="wide")

def process_key(driver, key):
    try:
        driver.get("https://account.vmix.com/login.aspx")
        driver.set_window_size(2576, 1416)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_txtRegistrationKey"))
        )
        
        driver.find_element(By.ID, "ContentPlaceHolder1_txtRegistrationKey").click()
        driver.find_element(By.ID, "ContentPlaceHolder1_txtRegistrationKey").clear()
        driver.find_element(By.ID, "ContentPlaceHolder1_txtRegistrationKey").send_keys(key)
        driver.find_element(By.ID, "ContentPlaceHolder1_cmdLogin").click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_mainContent_lblKey"))
        )
        
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        def get_text_or_none(element_id):
            element = soup.find(id=element_id)
            return element.text.strip() if element else 'N/A'
        
        def get_activation_details():
            table = soup.find(id='ContentPlaceHolder1_mainContent_tblMachines')
            if not table:
                return 'N/A'
            rows = table.find_all('tr')
            details = []
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    date = cols[0].text.strip()
                    description = cols[1].text.strip()
                    details.append(f"{date}:{description}")
            return ','.join(details)
        
        data = {
            'Registration Key': get_text_or_none('ContentPlaceHolder1_mainContent_lblKey'),
            'Edition': get_text_or_none('ContentPlaceHolder1_mainContent_lblEdition'),
            'Registered To': get_text_or_none('ContentPlaceHolder1_mainContent_lblEmail'),
            'Purchase Date': get_text_or_none('ContentPlaceHolder1_mainContent_lblPurchaseDate'),
            'Expiry Date': get_text_or_none('ContentPlaceHolder1_mainContent_lblExpiryDate'),
            'Install Date': get_text_or_none('ContentPlaceHolder1_mainContent_lblInstallDate'),
            'Download': get_text_or_none('ContentPlaceHolder1_mainContent_hDownload'),
            'Activate': get_activation_details()
        }
        
        return data
    
    except TimeoutException:
        data = {
            'Registration Key': 'N/A',
            'Edition': 'N/A',
            'Registered To': 'N/A',
            'Purchase Date': 'N/A',
            'Expiry Date': 'N/A',
            'Install Date': 'N/A',
            'Download': 'N/A',
            'Activate': 'N/A'
        }
        
        return data

def main():
    st.title('vMix License Key Processor')
    
    if 'uploaded_file' not in st.session_state:
        st.session_state['uploaded_file'] = None
    if 'processed_data' not in st.session_state:
        st.session_state['processed_data'] = None
    if 'joined_data' not in st.session_state:
        st.session_state['joined_data'] = None
    
    uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])
    
    if uploaded_file:
        st.session_state['uploaded_file'] = uploaded_file
        df = pd.read_excel(uploaded_file)
        columns = df.columns.tolist()
        
        st.sidebar.header("Settings")
        selected_column = st.sidebar.selectbox("Select the column with registration keys", columns)
        
        if st.sidebar.button("Start Processing",use_container_width=True,type='primary'):
            if selected_column:
                keys = df[selected_column].dropna().tolist()
                
                options = webdriver.ChromeOptions()
                options.add_argument('--headless')
                options.add_argument('--disable-gpu')
                options.add_argument('--window-size=1920x1080')
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)

                driver = webdriver.Chrome(options=options)
                
                progress_container = st.empty()
                results = []
                for i, key in enumerate(keys):
                    progress_container.progress((i + 1) / len(keys))
                    time.sleep(1.5)
                    data = process_key(driver, key)
                    results.append(data)
                
                driver.quit()
                
                result_df = pd.DataFrame(results)
                
                # Обработка данных, чтобы избежать ошибки IndexError
                def extract_version(download_text):
                    parts = download_text.split(' ')
                    return parts[1] if len(parts) > 1 else 'N/A'
                
                result_df['Available version'] = result_df['Download'].apply(extract_version)
                
                st.session_state['processed_data'] = result_df
                
                if st.session_state['processed_data'] is not None:
                    df = pd.read_excel(st.session_state['uploaded_file'])
                    
                    if selected_column in df.columns:
                        joined_df = pd.merge(df, result_df, left_on=selected_column, right_on='Registration Key', how='inner')
                        st.session_state['joined_data'] = joined_df
                        st.write("Joined Data")
                        #st.dataframe(joined_df)
                        st.data_editor(joined_df,height=600,num_rows="dynamic")

                        
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            st.download_button(
                                label="Download vmix.com data as CSV",
                                data=result_df.to_csv(index=False),
                                file_name='vmix_result.csv',
                                mime='text/csv',
                                key='download_vmix',
                                type='secondary', 
                                use_container_width=True
                            )
                        
                        with col2:
                            st.download_button(
                                label="Download joined data as CSV",
                                data=joined_df.to_csv(index=False),
                                file_name='joined_result.csv',
                                mime='text/csv',
                                key='download_joined',
                                type='secondary', 
                                use_container_width=True
                            )
                    else:
                        st.error(f"The selected column '{selected_column}' is not found in the uploaded data.")
            else:
                st.error("Please select a column with registration keys.")

if __name__ == "__main__":
    main()
