import datetime
from http.server import BaseHTTPRequestHandler
import json
import os
from api.services.get_news_bing import GetNewsBing
from api.models.postgres_database import PostgresDatabase
from api.services.scraping_news import ScrapingNews

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
        news_api = self.getNewsBing.get_customized_top_news(count=5)
        for news in news_api:
            title = news["name"]
            url = news["url"]
            self.database.insert_data("news", {"title": title, "url": url})
            
        time_22_hours_ago = datetime.now() - datetime.timedelta(hours=22)
        news_data = self.database.get_dairy_news("news", time_22_hours_ago)
        
        print(news_data)

        # news_contents = [self.scraping_news.fetch_article_content(news["url"]) for news in news_data]

        # print(news_contents)        

        response = {"message": "News data saved successfully."}
        response_json = json.dumps(response)

        # ヘッダーの設定
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        # レスポンスの送信
        self.wfile.write(response_json.encode('utf-8'))
        return
