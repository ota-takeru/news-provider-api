from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler
import json
import os

import urllib3
from api.services.get_news_bing import GetNewsBing
from api.models.postgres_database import PostgresDatabase
from api.services.scraping_news import ScrapingNews
import asyncio
from concurrent.futures import ThreadPoolExecutor

class handler(BaseHTTPRequestHandler):  
    def __init__(self, *args, **kwargs):
        self.getNewsBing = GetNewsBing()
        self.scraping_news = ScrapingNews()
        database_url = os.environ.get('POSTGRES_URL')
        self.database = PostgresDatabase(database_url)
        self.database.connect()
        self.database.create_table("news", "id SERIAL PRIMARY KEY, title TEXT, url TEXT")
        super().__init__(*args, **kwargs)

    def __del__(self):
        if hasattr(self, 'database'):
            self.database.close()
      

    def do_POST(self):
        time_22_hours_ago = datetime.utcnow()- timedelta(hours=22)
        formatted_time = time_22_hours_ago.strftime("%Y-%m-%dT%H:%M:%SZ")
        apikey = "a62af10295cc94b1a68c9b6b936e94a7"
        url = f"https://gnews.io/api/v4/top-headlines?&lang=ja&country=ja&max=10&from={formatted_time}&expand=content&apikey={apikey}"

        http = urllib3.PoolManager()
        response = http.request('GET', url)
        data = json.loads(response.data.decode('utf-8'))
        articles = data["articles"]
        print(len(articles))
        print(f"Type of article_data: {type(article_data)}")
            
        for i in range(len(articles)):
            article_data = {
                "title": articles[i]["title"],
                "url": articles[i]["url"],
                "content": articles[i]["content"]
            }
            self.database.insert_data("news", article_data)
        # loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(loop)
        # try:
        #     loop.run_until_complete(self.update_news())
        # finally:
        #     loop.close()  

        response = {"message": "News data saved successfully."}
        response_json = json.dumps(response)

        # ヘッダーの設定
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        # レスポンスの送信
        self.wfile.write(response_json.encode('utf-8'))
