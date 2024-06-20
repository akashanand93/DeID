import argparse
import os
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def download_large_pdf(url, output_path, session, headers):

    # Now make the request to download the PDF
    # response = session.get(url, headers=headers, cookies=cookies, stream=True)
    response = session.get(url, headers=headers, stream=True)

    # Check for successful response
    if response.status_code == 403:
        print("Forbidden access. Additional headers or cookies might still be needed.")
        return

    response.raise_for_status()  # Ensure we notice bad responses

    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:  # Filter out keep-alive new chunks
                f.write(chunk)

    print(f"Downloaded to: {output_path}")


def parse_all_and_download(headers, session, page_source, out_dir):
    # create the output directory if not present
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(page_source, "html.parser")

    # Find all PDF links
    pdf_links = []
    for link in soup.find_all("a", href=True):
        if "epdf" in link["href"]:
            pdf_url = link["href"]
            print(pdf_url)
            # pdf_url = urljoin(url, link['href'])
            pdf_links.append(pdf_url)

    # Download all PDFs
    for pdf_link in pdf_links:
        download_link = get_download_link(pdf_link, headers)
        print("DLINK", download_link)
        print(f"Downloading: {download_link}")
        out_path = os.path.join(out_dir, pdf_link.split("/")[-1] + ".pdf")
        download_large_pdf(download_link, out_path, session, headers)
        print(f"Downloaded to: {out_path}")

    print("All PDFs have been downloaded.")


def get_download_link(url, headers):
    # Set up Selenium WebDriver
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")  # Set window size
    options.add_argument(
        "--disable-dev-shm-usage"
    )  # Overcome limited resource problems
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )  # Set a user agent

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    # Open the webpage
    driver.get(url)

    # Wait for the page to load and locate the download button (modify the wait condition as needed)
    try:
        download_button = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.XPATH, "//a[contains(@href, 'download')]")
            )
        )
        download_link = download_button.get_attribute("href")
        print(f"Download link found: {download_link}")
    except Exception as e:
        print(f"Error finding download button: {e}")
        download_link = None
    finally:
        driver.quit()

    return download_link


def set_env_variables_for_selenium(url):

    # Set up Selenium WebDriver
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    # Open the webpage
    driver.get(url)

    # Allow some time for the page to load completely
    driver.implicitly_wait(20)

    # Extract cookies from Selenium WebDriver
    selenium_cookies = driver.get_cookies()

    # Create a requests session and set the cookies
    session = requests.Session()
    for cookie in selenium_cookies:
        session.cookies.set(cookie["name"], cookie["value"])

    # Set headers as captured from the browser (make sure these are accurate and complete)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://www.ahajournals.org/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cookie": "; ".join(
            [f"{cookie['name']}={cookie['value']}" for cookie in selenium_cookies]
        ),  # Set cookies header
    }

    # Get the page source and close the driver
    page_source = driver.page_source
    driver.quit()
    return headers, session, page_source


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download PDFs from a webpage.")
    parser.add_argument("--url", type=str, help="The URL to scrape PDFs from.")
    parser.add_argument(
        "--out_dir", type=str, help="Out directory path, have it in data lake."
    )

    args = parser.parse_args()

    url = "https://professional.heart.org/en/guidelines-statements-search#sort=%40guidelinepublishdate%20descending&numberOfResults=100&f:@guidelinecategory=[Guidelines]"
    out_dir = "/home/vinit/universe/data/lake/guidelines/aha/"

    # Do things with Selenium and headers and cookies
    headers, session, page_source = set_env_variables_for_selenium(args.url)

    # Parce the complete page and download all pdfs
    parse_all_and_download(headers, session, page_source, args.out_dir)
