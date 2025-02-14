from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
from gnews import GNews  # type: ignore


def set_cors_headers(handler, request_origin):
    allowed_origins = [
        'http://127.0.0.1:8080',  # 開発環境
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


class handler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):    
        self.gnews = GNews(language='ja', country='JP',max_results=10,)  # GNewsの初期化
        super().__init__(*args, **kwargs)

    def do_OPTIONS(self):
        self.send_response(200)
        request_origin = self.headers.get('Origin')
        set_cors_headers(self, request_origin)
        self.end_headers()

    def do_GET(self):
        query_string = self.path.split('?')[-1] if '?' in self.path else ''
        params = {param.split('=')[0]: param.split('=')[1] for param in query_string.split('&') if '=' in param}
        keyword = params.get('keyword', None)

        try:
            if keyword:
                news_data = self.gnews.get_news(keyword)
            else:
                news_data = self.gnews.get_top_news()

            serializable_news_data = []
            for index, item in enumerate(news_data):
                published_date = item.get("published date", None)
                if published_date:
                    if isinstance(published_date, str):
                        try:
                            published_date = datetime.fromisoformat(published_date)
                        except ValueError:
                            published_date = datetime.now()
                else:
                    published_date = datetime.now()
                
                serializable_item = {
                    "id": str(index),
                    "title": item.get("title", ""),
                    "published_at": published_date.isoformat(),
                    "url": item.get("link", ""),
                    "source_name": item.get("source", {}).get("name", "Unknown"),
                    "source_url": item.get("link", ""),
                    "content": item.get("description", "")
                }
                serializable_news_data.append(serializable_item)

            response = json.dumps(serializable_news_data, ensure_ascii=False)

        except Exception as e:
            response = json.dumps({"error": f"ニュースの取得中にエラーが発生しました: {e}"}, ensure_ascii=False)

        self.send_response(200)
        self.send_header("Content-type", "application/json; charset=utf-8")
        request_origin = self.headers.get('Origin')
        set_cors_headers(self, request_origin)
        self.end_headers()

        self.wfile.write(response.encode("utf-8"))
        return


# if __name__ == "__main__":
#     PORT = 8080
#     server = HTTPServer(("127.0.0.1", PORT), handler)
#     print(f"Server running on http://127.0.0.1:{PORT}")
#     server.serve_forever()
