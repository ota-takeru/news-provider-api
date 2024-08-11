from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime, timedelta

class handler(BaseHTTPRequestHandler):  
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
