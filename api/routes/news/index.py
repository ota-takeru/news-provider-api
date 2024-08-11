from http.server import BaseHTTPRequestHandler
import os
import json
from datetime import datetime, timedelta
from api.models.postgres_database import PostgresDatabase


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
            all_data = self.database.fetch_all("news")
            print("all_data", all_data)
        except Exception as e:
            news_data = []
            print(f"ニュースデータの取得中にエラーが発生しました: {e}")

         # datetimeオブジェクトを文字列に変換
        serializable_news_data = []
        for item in news_data:
            serializable_item = list(item)
            serializable_item[3] = serializable_item[3].isoformat()
            serializable_news_data.append(tuple(serializable_item))

        # JSON形式に変換
        response = json.dumps(serializable_news_data, ensure_ascii=False)

        # ヘッダーの設定
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        # レスポンスの送信
        self.wfile.write(response.encode("utf-8"))
        return
