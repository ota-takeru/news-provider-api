import requests
from bs4 import BeautifulSoup
import time
import random

class ScrapingNews:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def fetch_article_content(self, url):
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # メインコンテンツの抽出（この部分はウェブサイトの構造に応じて調整が必要）
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
            
            if main_content:
                paragraphs = main_content.find_all('p')
                content = '\n'.join([para.get_text().strip() for para in paragraphs if para.get_text().strip()])
            else:
                content = "メインコンテンツが見つかりませんでした。"
            
            return content
        except requests.RequestException as e:
            print(f"エラー: {url}のスクレイピング中に問題が発生しました - {str(e)}")
            return f"エラー: コンテンツの取得に失敗しました - {str(e)}"
        
    def scrape_with_rate_limit(self, urls, delay=1):
        contents = []
        for url in urls:
            content = self.fetch_article_content(url)
            contents.append(content)
            time.sleep(delay + random.uniform(0, 1))  # ランダムな遅延を追加
        return contents