import os
import time
import base64
import requests
import pandas as pd
from datetime import datetime
from scraper import Scraper
from urllib.parse import urljoin


class Parser:
    """A class to parse scraped data and handle various functionalities."""

    def __init__(self, scraped_data, base_url):
        """Initialize the Parser with scraped data and the base URL."""
        self.scraped_data = scraped_data
        self.base_url = base_url
        self.folder_name = self.create_folder()

    def create_folder(self):
        """Create a folder for storing parsed data based on the current timestamp."""
        filename_safe_base_url = ''.join(e for e in self.base_url if e.isalnum() or e == '_')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_name = f"{filename_safe_base_url}_{timestamp}"
        os.makedirs(folder_name, exist_ok=True)
        return folder_name

    def parse_data(self):
        """Parse the scraped data and save statistics, images, PDFs, and headings."""
        statistics_folder = os.path.join(self.folder_name, "statistics_data")
        os.makedirs(statistics_folder, exist_ok=True)
        statistics_path = os.path.join(statistics_folder, "statistics.xlsx")

        data_for_excel = {
            "Attribute": ["Image Count", "Word Count", "PDF Count", "Header Count"],
            "Value": [
                self.scraped_data.get("image_count", 0),
                self.scraped_data.get("word_count", 0),
                len(self.scraped_data.get("pdf_links", [])),
                self.scraped_data.get("header_count", 0)
            ]
        }

        df = pd.DataFrame(data_for_excel)
        df.to_excel(statistics_path, index=False)

        self.handle_images()
        self.handle_pdfs()
        self.handle_headings()

        return statistics_path

    def download_with_retry(self, url, path, base_url, max_retries=3):
        """Download a file from a URL with retry logic."""
        retry_count = 0
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        if not url.startswith('http'):
            url = urljoin(base_url, url)  # Resolves relative URLs

        while retry_count < max_retries:
            try:
                response = requests.get(url, headers=headers, stream=True)  # Use stream to avoid loading large files into memory
                response.raise_for_status()  # Check that the request was successful
                with open(path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192): 
                        if chunk:  # filter out keep-alive new chunks
                            f.write(chunk)
                return True
            except requests.exceptions.RequestException as e:
                print(f"Retry {retry_count + 1} for {url}: {e}")
                retry_count += 1
                time.sleep(1)  # Wait for 1 second before retrying
        return False
        
    def handle_images(self):
        """Download and save images from the scraped data."""
        images_folder = os.path.join(self.folder_name, "images")
        os.makedirs(images_folder, exist_ok=True)
        for i, img_url in enumerate(self.scraped_data.get("images", [])[:10], start=1):
            img_path = os.path.join(images_folder, f"{i}.jpg")
            self.download_with_retry(img_url, img_path, self.base_url)

    def handle_pdfs(self):
        """Download and save PDFs from the scraped data."""
        pdfs_folder = os.path.join(self.folder_name, "first_ten_pdfs")
        os.makedirs(pdfs_folder, exist_ok=True)
        for i, pdf_url in enumerate(self.scraped_data.get("pdf_links", [])[:10], start=1):
            pdf_path = os.path.join(pdfs_folder, f"pdf_{i}.pdf")
            self.download_with_retry(pdf_url, pdf_path, self.base_url)

    def handle_headings(self):
        """Save extracted headings from the scraped data."""
        headings_folder = os.path.join(self.folder_name, "headings")
        os.makedirs(headings_folder, exist_ok=True)
        headings_path = os.path.join(headings_folder, "headings.xlsx")

        flat_headings = []
        for heading_level, texts in self.scraped_data['headings'].items():
            for text in texts:
                flat_headings.append({'Heading Level': heading_level, 'Text': text})

        df_headings = pd.DataFrame(flat_headings)
        df_headings.to_excel(headings_path, index=False)
