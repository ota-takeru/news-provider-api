import asyncio
import aiohttp
from bs4 import BeautifulSoup
import random

class ScrapingNews:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    async def fetch_article_content(self, session, url):
        try:
            async with session.get(url, headers=self.headers, timeout=30) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                print(f"{url}のスクレイピングを始めます")
                
                # メインコンテンツの抽出（この部分はウェブサイトの構造に応じて調整が必要）
                main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
                
                if main_content:
                    paragraphs = main_content.find_all('p')
                    content = '\n'.join([para.get_text().strip() for para in paragraphs if para.get_text().strip()])
                else:
                    content = "メインコンテンツが見つかりませんでした。"
                
                return content
        except aiohttp.ClientError as e:
            print(f"エラー: {url}のスクレイピング中にクライアントエラーが発生しました - {str(e)}")
            return f"エラー: コンテンツの取得に失敗しました - {str(e)}"
        except asyncio.TimeoutError:
            print(f"エラー: {url}のスクレイピング中にタイムアウトが発生しました")
            return "エラー: スクレイピングがタイムアウトしました"
        except Exception as e:
            print(f"予期せぬエラー: {url}のスクレイピング中に問題が発生しました - {str(e)}")
            return f"予期せぬエラー: コンテンツの取得に失敗しました - {str(e)}"
        
    async def scrape_with_rate_limit(self, urls, delay=1, max_retries=3):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for url in urls:
                task = self.fetch_with_retry(session, url, max_retries)
                tasks.append(task)
                await asyncio.sleep(delay + random.uniform(0, 1))  # ランダムな遅延を追加
            return await asyncio.gather(*tasks)

    async def fetch_with_retry(self, session, url, max_retries):
        for attempt in range(max_retries):
            try:
                return await self.fetch_article_content(session, url)
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"最大リトライ回数に達しました: {url}")
                    return f"エラー: 最大リトライ回数に達しました - {str(e)}"
                print(f"リトライ中 ({attempt + 1}/{max_retries}): {url}")
                await asyncio.sleep(2 ** attempt)  # 指数バックオフ