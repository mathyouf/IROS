import csv
import os
import re
import time
import logging
import requests
# --- Setup Logging ---
log_file = '/Users/matto/Desktop/IROS/downloader.log'
# Clear the log file for a fresh start
if os.path.exists(log_file):
    os.remove(log_file)
logging.basicConfig(filename=log_file, 
                    level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def read_paper_titles(csv_path):
    """Reads paper titles from a CSV file."""
    titles = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header row
            for row in reader:
                if row:
                    titles.append(row[0])
    except FileNotFoundError:
        logging.error(f"CSV file not found at {csv_path}")
        print(f"Error: CSV file not found at {csv_path}")
    return titles

def sanitize_filename(title):
    """Sanitizes a string to be a valid filename."""
    return re.sub(r'[\\/:*?"<>|]', '', title)

def search_for_paper(title):
    """Searches for a paper's DOI using CrossRef, then finds a PDF with Unpaywall."""
    try:
        # 1. Search CrossRef for the DOI
        logging.info(f"Searching CrossRef for: {title}")
        crossref_url = 'https://api.crossref.org/works'
        params = {'query.bibliographic': title, 'rows': 1}
        response = requests.get(crossref_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data['status'] == 'ok' and data['message']['items']:
            doi = data['message']['items'][0]['DOI']
            logging.info(f"Found DOI: {doi}")
            
            # 2. Use Unpaywall to find the PDF from the DOI
            logging.info(f"Searching Unpaywall for DOI: {doi}")
            unpaywall_url = f'https://api.unpaywall.org/v2/{doi}?email=user@example.com'
            response = requests.get(unpaywall_url)
            response.raise_for_status()
            unpaywall_data = response.json()
            
            if unpaywall_data.get('best_oa_location') and unpaywall_data['best_oa_location'].get('url_for_pdf'):
                pdf_url = unpaywall_data['best_oa_location']['url_for_pdf']
                logging.info(f"Found PDF URL: {pdf_url}")
                return pdf_url
            else:
                logging.warning(f"No open access PDF found on Unpaywall for DOI: {doi}")
        else:
            logging.warning(f"No DOI found on CrossRef for: {title}")
            
    except requests.exceptions.RequestException as e:
        logging.error(f"API error for '{title}': {e}")
        print(f"An API error occurred for '{title}'")
    except Exception as e:
        logging.error(f"An unexpected error occurred for '{title}': {e}")
        print(f"An unexpected error occurred for '{title}'")
        
    return None

def download_pdf(url, filename):
    """Downloads a PDF from a URL."""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    try:
        logging.info(f"Downloading from {url}")
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logging.info(f"Successfully downloaded {filename}")
        print(f"Downloaded: {os.path.basename(filename)}")
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"Error downloading {url}: {e}")
        print(f"Error downloading {url}: {e}")
    return False

if __name__ == "__main__":
    csv_file = '/Users/matto/Desktop/IROS/topapers.csv'
    download_folder = '/Users/matto/Desktop/IROS/downloads'
    
    print(f"Script started. Logging to {log_file}")
    logging.info("--- Script Execution Started ---")
    
    paper_titles = read_paper_titles(csv_file)
    if not paper_titles:
        print("No paper titles found. Exiting.")
        logging.warning("No paper titles found in CSV. Exiting script.")
    else:
        print(f"Found {len(paper_titles)} paper titles.")
        for i, title in enumerate(paper_titles):
            print(f"\n--- Processing paper {i+1}/{len(paper_titles)}: {title[:70]}... ---")
            
            sanitized_title = sanitize_filename(title)
            filename = os.path.join(download_folder, f"{sanitized_title}.pdf")

            if os.path.exists(filename):
                logging.info(f"File already exists: {filename}. Skipping.")
                print("PDF already exists. Skipping.")
                continue

            pdf_url = search_for_paper(title)
            if pdf_url:
                logging.info(f"PDF URL found: {pdf_url}")
                download_pdf(pdf_url, filename)
            else:
                print("No open access PDF found.")
            
            # Respectful delay for the APIs
            time.sleep(2)
            
        print("\nScript finished.")
        logging.info("--- Script Execution Finished ---")
