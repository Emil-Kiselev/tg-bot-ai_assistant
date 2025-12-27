import requests
from bs4 import BeautifulSoup
import re

urls = [
    #your url's 
]

def clean_text(text):
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) < 50:
        return ""
    return text

unique_lines = set()
result = ""

for url in urls:
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup.find_all(["p", "li", "h2", "h3", "h4", "span", "article"]):
            t = clean_text(tag.get_text(" ", strip=True))
            if t and t not in unique_lines:
                unique_lines.add(t)
                result += t + "\n"
    except Exception as e:
        print(fError {url}: {e}")

with open("custom_data.txt", "w", encoding="utf-8") as f:
    f.write(result)
