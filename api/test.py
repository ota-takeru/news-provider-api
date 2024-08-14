


from datetime import datetime, timedelta
import os

from api.models.postgres_database import PostgresDatabase


database_url = os.environ.get("POSTGRES_URL")
database =  PostgresDatabase(database_url)

time_22_hours_ago = datetime.now() - timedelta(hours=22)
try:
    news_data = database.get_daily_news("news", time_22_hours_ago)
    if not news_data:
        news_data = []
        print("ニュースデータが見つかりませんでした。")
    # all_data = self.database.fetch_all("news")
    # print("all_data", all_data)
except Exception as e:
    news_data = []
    print(f"ニュースデータの取得中にエラーが発生しました: {e}")

         # datetimeオブジェクトを文字列に変換
serializable_news_data = []
for item in news_data:
    print(item)
    serializable_item = {
        "id": item[0],
        "title": item[1],
        "content": item[5],
        # "published_date": item[3].isoformat(),
        # 他のフィールドがある場合は追加
    }
    serializable_news_data.append(serializable_item)