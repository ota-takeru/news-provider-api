from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler
import json
import os
import urllib3
from api.models.postgres_database import PostgresDatabase

class handler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        try:
            database_url = os.environ.get("POSTGRES_URL")
            self.database = PostgresDatabase(database_url)
            self.database.connect()
            super().__init__(*args, **kwargs)
        except Exception as e:
            print(f"Error during initialization: {str(e)}")
            raise

    def __del__(self):
        if hasattr(self, "database"):
            self.database.close()

    def do_POST(self):
        try:
            time_24_hours_ago = datetime.now(timezone.utc) - timedelta(hours=24)
            formatted_time = time_24_hours_ago.strftime("%Y-%m-%dT%H:%M:%SZ")+ "Z"

            apikey = os.environ.get("GNEWS_API_KEY")
            if not apikey:
                raise ValueError("GNEWS_API_KEY not found in environment variables")
            url = f"https://gnews.io/api/v4/top-headlines?&lang=ja&country=jp&max=20&expand=content&apikey={apikey}"
            # url = f"https://gnews.io/api/v4/top-headlines?&lang=ja&country=jp&max=1&from={formatted_time}&expand=content&apikey={apikey}"

            apikey = os.environ.get("GNEWS_API_KEY")
            if not apikey:
                raise ValueError("GNEWS_API_KEY not found in environment variables")
            # url = f"https://gnews.io/api/v4/top-headlines?&lang=ja&country=jp&max=1&expand=content&apikey={apikey}"
            url = f"https://gnews.io/api/v4/top-headlines?lang=ja&country=jp&max=1&from={formatted_time}&expand=content&apikey={apikey}"


            http = urllib3.PoolManager()
            response = http.request("GET", url, timeout=10.0)
            data = json.loads(response.data.decode("utf-8"))

            print(data['totalArticles'])
            
            if "articles" not in data:
                raise KeyError("'articles' key not found in API response")
            
            articles = data["articles"]
            print(f"Received {len(articles)} articles from GNews API")
            print(articles[0])

            for article in articles:
                article_data = {
                    "title": article.get("title", ""),
                    "url": article.get("url", ""),
                    "content": article.get("content", ""),
                    "source_name": article.get("source", {}).get("name", ""),
                    "source_url": article.get("source", {}).get("url", ""),
                }
                self.database.insert_data("news", article_data)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"message": "News data saved successfully."}).encode("utf-8"))
        
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {str(e)}")
            self.send_error(500, "Internal Server Error")
        except KeyError as e:
            print(f"Key error: {str(e)}")
            self.send_error(500, "Internal Server Error")
        except urllib3.exceptions.RequestError as e:
            print(f"Error during HTTP request: {str(e)}")
            self.send_error(500, "Internal Server Error")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            self.send_error(500, "Internal Server Error")