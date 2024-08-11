import requests
from bs4 import BeautifulSoup

class ScrapingNews:
    def __init__(self):
        pass
        
    def fetch_article_content(self, url):
        response = requests.get(url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # title = soup.title.string if soup.title else "No Title Found"
            
            paragraphs = soup.find_all('p')
            content = '\n'.join([para.get_text() for para in paragraphs])
        else:
            # title = "Error fetching title"
            content = "Error fetching content"
        
        return content