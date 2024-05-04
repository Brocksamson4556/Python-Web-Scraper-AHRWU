import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

class Scraper:
    """A class to scrape content from a given URL."""

    def __init__(self, url):
        """Initialize the Scraper with the URL to scrape."""
        self.url = url
        self.content = ""
        self.soup = None
        self.scraped_data = {}

    def fetch_content(self):
        """Fetches the content from the URL and parses it using BeautifulSoup."""
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            self.content = response.text
            self.soup = BeautifulSoup(self.content, 'html.parser')
            self.scraped_data['soup'] = self.soup
            self.scraped_data['headings'] = self.extract_headings()
            self.extract_data()  # Extract additional data immediately after parsing
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error fetching content from {self.url}: {e}")
            return False

    def extract_headings(self):
        """Extracts headings from the parsed HTML soup."""
        headings = {}
        for level in range(1, 7):
            tags = self.soup.find_all(f'h{level}')
            headings[level] = [tag.text.strip() for tag in tags]
        return headings

    def extract_data(self):
        """Extracts various data from the parsed HTML soup."""
        if not self.soup:
            print("Content has not been fetched. Call fetch_content() first.")
            return

        images = self.soup.find_all('img')
        words = self.soup.get_text().split()
        links = self.soup.find_all('a', href=True)
        pdfs = []

        for link in links:
            url = link['href']
            parsed_url = urlparse(url)
            if 'google.com' in parsed_url.netloc:
                query_params = parse_qs(parsed_url.query)
                possible_pdf_url = query_params.get('q', [])
                if possible_pdf_url and possible_pdf_url[0].endswith('.pdf'):
                    pdfs.append(possible_pdf_url[0])
            elif url.endswith('.pdf'):
                pdfs.append(url)

        headers = self.soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

        self.scraped_data.update({
            "image_count": len(images),
            "word_count": len(words),
            "pdf_links": pdfs,
            "header_count": len(headers),
            "images": [img['src'] for img in images if img.get('src')]
        })
