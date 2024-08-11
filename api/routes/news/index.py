from http.server import BaseHTTPRequestHandler
import os
import json
from datetime import datetime, timedelta
from api.models.postgres_database import PostgresDatabase

class handler(BaseHTTPRequestHandler):  
    def __init__(self, *args, **kwargs):
        database_url = os.environ.get('DATABASE_URL')

        self.database = PostgresDatabase(database_url)
        self.database.connect() 
        super().__init__(*args, **kwargs)

    def __del__(self):
        if hasattr(self, 'database'):
            self.database.close()

    def do_GET(self):
        time_22_hours_ago = datetime.now() - timedelta(hours=22)
        news_data = self.database.get_dairy_news("news", time_22_hours_ago)


        # JSON形式に変換
        response = json.dumps(news_data, ensure_ascii=False)

        # ヘッダーの設定
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.end_headers()

        # レスポンスの送信
        self.wfile.write(response.encode('utf-8'))
        return
