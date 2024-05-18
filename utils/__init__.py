
import time
from selenium.webdriver.common.by import By
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import torch

def are_urls_same(url1, url2):
    # normalize urls
    url1 = url1.replace('www.', '').rstrip('/')
    url2 = url2.replace('www.', '').rstrip('/')

    url1 = urlparse(url1.lower())
    url2 = urlparse(url2.lower())
    return (url1.netloc == url2.netloc) and (url1.path == url2.path) and (url1.scheme == url2.scheme)

def url_exists_in_set(visited, url):
    url = url.split('#')[0].split('?')[0].replace('www.', '')
    for visited_url in visited:
        visited_url = visited_url.split('#')[0].split('?')[0].replace('www.', '')
        if are_urls_same(visited_url, url):
            return True
        
        # if domain is different return True
        if urlparse(visited_url).netloc != urlparse(url).netloc:
            return True
        
    return False

def scrape_site(driver, url, visited=None, count:int=2):

    # normalize url
    url = url.split('#')[0].split('?')[0]
    url = url.replace('www.', '')

    if visited is None:
        visited = set()
    if url in visited:
        return []
    print(f"Visiting: {url}")
    visited.add(url)
    driver.get(url)
    time.sleep(2)  # Adjust timing based on the website's response time
    content = driver.page_source
    links = driver.find_elements(By.TAG_NAME, 'a')
    links_hrefs = [link.get_attribute('href') for link in links]
    data = {}
    data[str(url)] = str(content)
    for href in links_hrefs:
        if href and not url_exists_in_set(visited, href):
            if(len(visited) >= count):
                break # Stop scraping after visiting max_pages

            data = {**data, **scrape_site(driver, href, visited, count)}
            # data.extend(scrape_site(driver, href, visited))
    return data

def html_to_text(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text()

def embed_text(text):
    inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True)
    with torch.no_grad():
        embeddings = model(**inputs).last_hidden_state.mean(dim=1)
    return embeddings.numpy()