from http.server import BaseHTTPRequestHandler
import os
import json
from datetime import datetime, timedelta
from api.models.postgres_database import PostgresDatabase

def set_cors_headers(handler, request_origin):
    allowed_origins = [
        'http://localhost',  # 開発環境
        'https://your-flutter-app.com',  # 本番環境のWebアプリ
        None  # モバイル/デスクトップアプリからのリクエスト用
    ]
    
    if request_origin in allowed_origins or request_origin is None:
        if request_origin:
            handler.send_header('Access-Control-Allow-Origin', request_origin)
        else:
            handler.send_header('Access-Control-Allow-Origin', '*')  # モバイル/デスクトップアプリ用
    else:
        handler.send_header('Access-Control-Allow-Origin', 'https://your-flutter-app.com')  # デフォルトのオリジン
    
    handler.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    handler.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')

def do_OPTIONS(self):
    self.send_response(200)
    request_origin = self.headers.get('Origin')
    set_cors_headers(self, request_origin)
    self.end_headers()


class handler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        database_url = os.environ.get("POSTGRES_URL")

        self.database = PostgresDatabase(database_url)
        self.database.connect()
        super().__init__(*args, **kwargs)

    def __del__(self):
        if hasattr(self, "database"):
            self.database.close()

    def do_GET(self):
        time_22_hours_ago = datetime.now() - timedelta(hours=22)
        try:
            news_data = self.database.get_daily_news("news", time_22_hours_ago)
            if not news_data:
                news_data = []
                print("ニュースデータが見つかりませんでした。")
            # all_data = self.database.fetch_all("news")
            # print("all_data", all_data) 
        except Exception as e:
            news_data = []
            print(f"ニュースデータの取得中にエラーが発生しました: {e}")

        print(news_data)
        #  datetimeオブジェクトを文字列に変換
        serializable_news_data = []
        for item in news_data:
            serializable_item = {
                "id": item["id"], 
                "title": item["title"],
                "content": item["content"],
                # "published_date": item["published_date"].isoformat(),
                # 他のフィールドがある場合は追加
            }
            serializable_news_data.append(serializable_item)

        # response = json.dumps(news_data, ensure_ascii=False)
        response = json.dumps(serializable_news_data, ensure_ascii=False)

        # ヘッダーの設定
        self.send_response(200)
        self.send_header("Content-type", "application/json; charset=utf-8")
        request_origin = self.headers.get('Origin')
        set_cors_headers(self, request_origin)
        self.end_headers()

        # レスポンスの送信
        self.wfile.write(response.encode("utf-8"))
        return
