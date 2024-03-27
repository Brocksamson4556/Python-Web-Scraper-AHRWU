import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
from urllib.parse import urljoin, urlparse


def scrape_data(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        title = soup.title.text if soup.title else 'No Title Found'
        headings = [h.text.strip() for h in soup.find_all(['h1', 'h2', 'h3'])]
        paragraphs = [p.text.strip() for p in soup.find_all('p')]
        images_urls = [img['src'] for img in soup.find_all('img') if 'src' in img.attrs]
        links = [a['href'] for a in soup.find_all('a', href=True)]
        contacts = [a['href'] for a in soup.find_all('a', href=True) if 'mailto:' in a['href']]
        reviews = [review.text.strip() for review in soup.find_all(class_=re.compile("(review|comment)"))]

        # Download images from the collected URLs
        download_images(images_urls, url)

        return {
            'title': title,
            'headings': headings,
            'paragraphs': paragraphs,
            'images': images_urls,
            'links': links,
            'contacts': contacts,
            'reviews': reviews
        }
    except Exception as e:
        print(f"Error scraping data from {url}: {e}")
        return None


def download_images(image_urls, base_url):
    for i, img_url in enumerate(image_urls):
        try:
            img_url = urljoin(base_url, img_url)
            filename = os.path.join("downloaded_images", os.path.basename(urlparse(img_url).path))
            if not os.path.isfile(filename):  # Avoid downloading if already exists
                with requests.get(img_url, stream=True) as r:
                    r.raise_for_status()
                    with open(filename, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
            print(f"Downloaded {filename}")
        except Exception as e:
            print(f"Error downloading {img_url}: {e}")


def sanitize_worksheet_name(name):
    """Sanitize the URL to be used as a worksheet name."""
    # Remove http:// or https://
    sanitized_name = re.sub(r'https?://', '', name)
    # Replace invalid characters with underscore
    sanitized_name = re.sub(r'[\\/*?:"<>|\[\]]', '_', sanitized_name)
    # Truncate to the maximum length allowed by Excel (31 characters)
    return sanitized_name[:31]


def write_to_excel(data, output_file):
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        for url, scraped_data in data:
            flat_data = []
            for key, values in scraped_data.items():
                for value in values:
                    flat_data.append([url, key, value])
            df = pd.DataFrame(flat_data, columns=['Website', 'Type', 'Data'])  # Dummy headers
            # Use a sanitized version of the URL as the worksheet name
            worksheet_name = sanitize_worksheet_name(url)
            df.to_excel(writer, sheet_name=worksheet_name, index=False)


def scrape_analyze_and_save():
    urls = entry.get().split(',')
    data = []
    total_urls = len(urls)
    progress_bar['maximum'] = total_urls

    # Regex for URL validation
    reg_exp = r"https?:\/\/(?:www\.)?[a-zA-Z0-9._\/-]+(?:[?&][a-zA-Z0-9=_-]+)*"

    for index, url in enumerate(urls):
        if re.match(reg_exp, url):
            print("Valid URL presented. Scraping operation will proceed.")
            scraped_data = scrape_data(url)
            if scraped_data:
                data.append((url, scraped_data))
        else:
            print("Invalid URL. Please try again.")
            continue  # Skip to the next URL

        # Update progress bar after each URL is processed
        progress_bar['value'] = index + 1
        root.update_idletasks()

    if data:
        output_file = filedialog.asksaveasfilename(defaultextension=".xlsx")
        if output_file:
            write_to_excel(data, output_file)
            messagebox.showinfo("Success", "Data scraped and saved successfully.")
    else:
        messagebox.showerror("Error", "Failed to scrape data. Check URL")
    # Reset progress bar
    progress_bar['value'] = 0


def on_enter(event):
    root.configure(bg="blue")


def on_leave(event):
    root.configure(bg="black")


def exit_application():
    root.destroy()


"""Image download directory"""
os.makedirs("downloaded_images", exist_ok=True)

root = tk.Tk()
root.title("Website Data Scraper and Visualizer")

base_font_size = 10
large_font = ('Arial', base_font_size * 2)

root.configure(bg="black")
root.state('zoomed')

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
root.grid_columnconfigure(3, weight=1)

# A greeting banner
banner = tk.Label(root, text="Welcome to the Python Web Scraper!", foreground="#B71C1C", bg="black",
                  font=("Arial", int(base_font_size * 2.5))
                  )
banner.grid(row=0, column=0, columnspan=4, pady=10, sticky="ew")

# URL input
label = tk.Label(root, text="Enter website URLs (comma-separated):", fg="black", bg="grey",
                 font=large_font, padx=100, pady=10)
label.grid(row=1, column=1, sticky="E", padx=(10, 10), pady=50)

entry = tk.Entry(root, width=50, font=large_font)
entry.grid(row=1, column=2, sticky="EW", pady=50, ipady=10)

# Progress bar
progress_bar = ttk.Progressbar(root, orient="horizontal", length=250, mode="determinate")
progress_bar.grid(row=5, column=1, columnspan=2, sticky='EW', padx=10, pady=400, ipadx=200, ipady=20)

# Scrape, Analyze, and Save button
scrape_button = tk.Button(root, text="Scrape, Analyze, and Save", command=scrape_analyze_and_save,
                          bg="orange", font=large_font)
scrape_button.grid(row=4, column=1, columnspan=2, pady=15, padx=(10, 10), ipadx=100, ipady=20)

# Exit button
exit_button = tk.Button(root, text="Exit", command=exit_application, bg="red", font=large_font)
exit_button.grid(row=4, column=2, columnspan=2, pady=10, padx=(20, 20), ipadx=10, ipady=20)

root.bind("<Enter>", on_enter)
root.bind("<Leave>", on_leave)

root.mainloop()