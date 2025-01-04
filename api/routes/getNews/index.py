from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
from gnews import GNews  # type: ignore

def set_cors_headers(handler, request_origin):
    allowed_origins = [
        'http://127.0.0.1:8080',   # 開発環境
        'https://voice-news-pink.vercel.app/',  # 本番環境のWebアプリ
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
        self.gnews = GNews(language='ja', country='JP')  # GNewsの初期化
        super().__init__(*args, **kwargs)

    def do_GET(self):
        # クエリパラメータからキーワードを取得
        query_string = self.path.split('?')[-1] if '?' in self.path else ''
        params = {param.split('=')[0]: param.split('=')[1] for param in query_string.split('&') if '=' in param}
        keyword = params.get('keyword', None)

        try:
            # ニュースの取得
            if keyword:
                news_data = self.gnews.get_news(keyword)
            else:
                news_data = self.gnews.get_top_news()

            # ニュースデータを指定された形式に変換
            serializable_news_data = []
            for index, item in enumerate(news_data):
                serializable_item = {
                    "id": str(index),  # IDをインデックスとして代用
                    "title": item.get("title", ""),
                    "published_at": item.get("published date", datetime.now()).isoformat() if "published date" in item else datetime.now().isoformat(),
                    "url": item.get("link", ""),
                    "source_name": item.get("source", {}).get("name", "Unknown"),
                    "source_url": item.get("link", ""),  # ソースURLがないためリンクを代用
                    "content": item.get("description", "")
                }
                serializable_news_data.append(serializable_item)

            response = json.dumps(serializable_news_data, ensure_ascii=False)

        except Exception as e:
            # エラー発生時の処理
            response = json.dumps({"error": f"ニュースの取得中にエラーが発生しました: {e}"}, ensure_ascii=False)

        # ヘッダーの設定
        self.send_response(200)
        self.send_header("Content-type", "application/json; charset=utf-8")
        request_origin = self.headers.get('Origin')
        set_cors_headers(self, request_origin)
        self.end_headers()

        # レスポンスの送信
        self.wfile.write(response.encode("utf-8"))
        return
