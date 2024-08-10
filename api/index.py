from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        # ニュース記事とタイトルのサンプルデータ
        news_data = [
            {"title": "Sample News 1", "content": "This is the content of sample news 1."},
            {"title": "Sample News 2", "content": "This is the content of sample news 2."},
            {"title": "Sample News 3", "content": "This is the content of sample news 3."},
            {"title": "Sample News 4", "content": "This is the content of sample news 4."},
            {"title": "Sample News 5", "content": "This is the content of sample news 5."}
        ]

        # JSON形式に変換
        response = json.dumps(news_data, ensure_ascii=False)

        # ヘッダーの設定
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.end_headers()

        # レスポンスの送信
        self.wfile.write(response.encode('utf-8'))
        return
