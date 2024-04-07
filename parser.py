import os
import pandas as pd
from datetime import datetime
import requests
import base64
import time

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
        data_for_excel = {
            "Attribute": ["Image Count", "Word Count", "PDF Count", "Header Count"],
            "Value": [
                self.scraped_data.get("image_count", 0),
                self.scraped_data.get("word_count", 0),
                len(self.scraped_data.get("pdf_links", [])),
                self.scraped_data.get("header_count", 0)
            ]
        }

        # Print word count and image count for debugging
        print("Word Count from Scraper:", self.scraped_data.get("word_count", 0))
        print("Image Count from Scraper:", self.scraped_data.get("image_count", 0))

        df = pd.DataFrame(data_for_excel)
        statistics_path = os.path.join(self.folder_name, "statistics.xlsx")
        df.to_excel(statistics_path, index=False)

        # Handle additional functionality for images, PDFs, and headings
        self.handle_images()
        self.handle_pdfs()
        self.handle_headings()

        return statistics_path

    def download_with_retry(self, url, path, base_url, max_retries=3):
        """Download a file from a URL with retry logic."""
        if url.startswith('data:image'):
            # Handle base64-encoded images
            header, encoded = url.split(',', 1)
            data = base64.b64decode(encoded)
            with open(path, 'wb') as file:
                file.write(data)
            return True
        else:
            # Logic for handling regular image URLs
            retry_count = 0
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            }
            if not url.startswith('http'):
                from urllib.parse import urljoin
                url = urljoin(base_url, url)
            while retry_count < max_retries:
                try:
                    response = requests.get(url, headers=headers)
                    if response.status_code == 200:
                        with open(path, 'wb') as file:
                            file.write(response.content)
                        return True
                    else:
                        raise requests.exceptions.HTTPError(f"Status code: {response.status_code}")
                except requests.exceptions.RequestException as e:
                    print(f"Retry {retry_count + 1} for {url}: {e}")
                    time.sleep(1)  # Wait for 1 second before retrying
                    retry_count += 1
            return False

    def handle_images(self):
        """Download and save images from the scraped data."""
        images_folder = os.path.join(self.folder_name, "first_ten_images")
        os.makedirs(images_folder, exist_ok=True)
        for i, img_url in enumerate(self.scraped_data.get("images", [])[:10], start=1):
            img_path = os.path.join(images_folder, f"{self.folder_name}_image_{i}.jpg")
            self.download_with_retry(img_url, img_path, self.base_url)

    def handle_pdfs(self):
        """Download and save PDFs from the scraped data."""
        pdfs_folder = os.path.join(self.folder_name, "first_ten_pdfs")
        os.makedirs(pdfs_folder, exist_ok=True)
        for i, pdf_url in enumerate(self.scraped_data.get("pdf_links", [])[:10], start=1):
            pdf_path = os.path.join(pdfs_folder, f"{self.folder_name}_pdf_{i}.pdf")
            self.download_with_retry(pdf_url, pdf_path, self.base_url)

    def handle_headings(self):
        """Save extracted headings from the scraped data."""
        headings_folder = os.path.join(self.folder_name, "headings_data")
        os.makedirs(headings_folder, exist_ok=True)
        headings_path = os.path.join(headings_folder, "headings.xlsx")

        flat_headings = []
        for heading_level, texts in self.scraped_data['headings'].items():
            for text in texts:
                flat_headings.append({'Heading Level': heading_level, 'Text': text})

        df_headings = pd.DataFrame(flat_headings)
        df_headings.to_excel(headings_path, index=False)
