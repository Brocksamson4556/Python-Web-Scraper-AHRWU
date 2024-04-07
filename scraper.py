import requests
from bs4 import BeautifulSoup

class Scraper:
    """A class to scrape content from a given URL."""

    def __init__(self, url):
        """Initialize the Scraper with the URL to scrape."""
        self.url = url
        self.content = ""  # Initialize content to an empty string
        self.soup = None  # Initialize soup to None
        self.scraped_data = {}  # Initialize scraped_data as an empty dictionary

    def fetch_content(self):
        """Fetches the content from the URL and parses it using BeautifulSoup."""
        try:
            response = requests.get(self.url)
            response.raise_for_status()  # Raises HTTPError for bad responses
            self.content = response.text
            self.soup = BeautifulSoup(self.content, 'html.parser')
            # Store the parsed soup and headings in the scraped_data dictionary
            self.scraped_data['soup'] = self.soup
            self.scraped_data['headings'] = self.extract_headings()  # Extract headings
        except requests.exceptions.RequestException as e:
            print(f"Error fetching content from {self.url}: {e}")
            return False
        return True

    def extract_headings(self):
        """Extracts headings from the parsed HTML soup."""
        headings = {}
        # Iterate over heading levels from h1 to h6
        for level in range(1, 7):
            tags = self.soup.find_all(f'h{level}')  # Find all tags of the current heading level
            # Extract text from each tag and store in the headings dictionary
            headings[level] = [tag.text.strip() for tag in tags]
        return headings

    def extract_data(self):
        """Extracts various data from the parsed HTML soup."""
        if not self.soup:
            print("Content has not been fetched. Call fetch_content() first.")
            return {}

        # Extract images, words, PDF links, and headers from the parsed HTML soup
        images = self.soup.find_all('img')
        image_count = len(images)
        words = self.soup.get_text().split()
        word_count = len(words)

        # Print word count and image count for debugging
        print("Word Count:", word_count)
        print("Image Count:", image_count)

        pdf_links = [a['href'] for a in self.soup.find_all('a', href=True) if a['href'].endswith('.pdf')]
        headers = self.soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        header_count = len(headers)

        return {
            "image_count": image_count,
            "word_count": word_count,
            "pdf_links": pdf_links,
            "header_count": header_count,
            "images": [img['src'] for img in images if img.get('src')]
        }
