from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler
import json
import os
import urllib3
from api.models.postgres_database import PostgresDatabase

class handler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        database_url = os.environ.get("POSTGRES_URL")
        self.database = PostgresDatabase(database_url)
        self.database.connect()
        # self.database.create_table(
        #     "news", "id SERIAL PRIMARY KEY, title TEXT, url TEXT, content TEXT, source_name TEXT, source_url TEXT"
        # )
        super().__init__(*args, **kwargs)

    def __del__(self):
        if hasattr(self, "database"):
            self.database.close()

    def do_POST(self):
        time_24_hours_ago = datetime.now(timezone.utc) - timedelta(hours=24)
        formatted_time = time_24_hours_ago.strftime("%Y-%m-%dT%H:%M:%SZ")
        apikey = os.environ.get("a62af10295cc94b1a68c9b6b936e94a7")
        # apikey = os.environ.get("GNEWS_API_KEY")
        url = f"https://gnews.io/api/v4/top-headlines?&lang=ja&country=ja&max=20&from={formatted_time}&expand=content&apikey={apikey}"

        http = urllib3.PoolManager()
        response = http.request("GET", url)
        data = json.loads(response.data.decode("utf-8"))
        articles = data["articles"]

        for article in articles:
            article_data = {
                "title": article["title"],
                "url": article["url"],
                "content": article["content"],
                "source_name": article["source"]["name"],
                "source_url": article["source"]["url"],
            }
            self.database.insert_data("news", article_data)

        response = {"message": "News data saved successfully."}
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode("utf-8"))