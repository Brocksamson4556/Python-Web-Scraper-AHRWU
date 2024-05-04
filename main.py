import tkinter as tk
from tkinter import messagebox
import re
from scraper import Scraper
from Parser_1 import Parser

class WebScraperApp:
    """A class representing the main application window."""

    def __init__(self, root):
        """Initialize the application with the root window."""
        self.root = root
        self.setup_gui()

    def setup_gui(self):
        """Set up the graphical user interface."""
        self.root.title("Web Scraper Tool")
        self.root.geometry('500x350')  # Set fixed window size
        self.root.resizable(False, False)
        self.root.config(bg="#CEE6F2")

        # URL entry frame
        self.url_frame = tk.Frame(self.root, bg="#CEE6F2")
        self.url_frame.pack(pady=20, padx=20, fill="x")
        self.url_label = tk.Label(self.url_frame, text="URL:", bg="#CEE6F2")
        self.url_label.pack(side=tk.LEFT, padx=(0, 10))
        self.url_entry = tk.Entry(self.url_frame, width=40, bg="#FFFFFF", fg="#CEE6F2", highlightbackground="#FFFFFF", highlightthickness=5)
        self.url_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.validate_button = tk.Button(self.url_frame, text="Load URL", bg="#E9B796", highlightbackground="#FFFFFF", highlightthickness=5, command=self.validate_and_fetch)
        self.validate_button.pack(side=tk.LEFT, padx=(10, 0))

        # Action button frame
        self.action_frame = tk.Frame(self.root, bg="#CEE6F2")
        self.action_frame.pack(pady=10)
        self.analyze_button = tk.Button(self.action_frame, text="Scrape, Analyze, and Save", bg="#E3867D", highlightbackground="#FFFFFF", highlightthickness=5, command=self.analyze_data)
        self.analyze_button.pack(side=tk.LEFT, padx=5)
        self.exit_button = tk.Button(self.action_frame, text="Exit", bg="#962E2A", highlightbackground="#FFFFFF", highlightthickness=5, command=self.root.quit)
        self.exit_button.pack(side=tk.LEFT, padx=5)

    def validate_and_fetch(self):
        """Validate the entered URL and fetch its content."""
        url = self.url_entry.get()
        if not re.match(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', url):
            messagebox.showerror("Error", "Invalid URL. Please enter a valid URL.")
            return

        self.scraper = Scraper(url)
        if self.scraper.fetch_content():
            messagebox.showinfo("Success", "Content fetched successfully.")
        else:
            messagebox.showerror("Error", "Failed to fetch content.")

    def analyze_data(self):
        """Analyze the fetched content and display success or error messages."""
        if not hasattr(self, 'scraper') or not self.scraper.soup:
            messagebox.showerror("Error", "No content to analyze. Fetch content first.")
            return

        data = self.scraper.scraped_data
        parser = Parser(data, self.scraper.url)
        statistics_path = parser.parse_data()
        messagebox.showinfo("Success", f"Data saved successfully. Check the folder: {statistics_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WebScraperApp(root)
    root.mainloop()
