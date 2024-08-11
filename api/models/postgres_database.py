
import datetime
import psycopg2
from psycopg2 import sql

class PostgresDatabase:
    def __init__(self, db_url):
        self.db_url = db_url
        self.conn = None
        self.cursor = None

    def connect(self):
        """データベースに接続"""
        try:
            self.conn = psycopg2.connect(self.db_url)
            self.cursor = self.conn.cursor()
            print("Connected to the database.")
        except Exception as e:
            print(f"Failed to connect to the database: {e}")
            raise

    def close(self):
        """接続を閉じる"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("Database connection closed.")

    def create_table(self, table_name: str, columns: str):
        """
        テーブルを作成
        :param table_name: テーブル名
        :param columns: カラム定義（例: "id SERIAL PRIMARY KEY, title TEXT, content TEXT "
        """
        columns += ", created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        try:
            # テーブルが存在するかチェック
            check_table_query = sql.SQL("SELECT to_regclass({table})").format(
                table=sql.Literal(table_name)
            )
            self.cursor.execute(check_table_query)
            table_exists = self.cursor.fetchone()[0]

            if table_exists:
                print(f"テーブル '{table_name}' はすでに存在します。")
            else:
                create_table_query = sql.SQL("CREATE TABLE IF NOT EXISTS {table} ({columns})").format(
                    table=sql.Identifier(table_name),
                    columns=sql.SQL(columns)
                )
                self.cursor.execute(create_table_query)
                self.conn.commit()
                print(f"テーブル '{table_name}' が正常に作成されました。")
        except Exception as e:
            print(f"テーブルの作成に失敗しました: {e}")
            self.conn.rollback()
            raise

    def insert_data(self, table_name: str, data: dict):
        """
        データを挿入
        :param table_name: テーブル名
        :param data: 挿入するデータ（辞書形式、例: {"title": "Example Title", "content": "Example content"}
        """
        try:
            columns = data.keys()
            values = [data[column] for column in columns]

            insert_query = sql.SQL("INSERT INTO {table} ({fields}) VALUES ({placeholders})").format(
                table=sql.Identifier(table_name),
                fields=sql.SQL(',').join(map(sql.Identifier, columns)),
                placeholders=sql.SQL(',').join(sql.Placeholder() * len(columns))
            )
            self.cursor.execute(insert_query, values)
            self.conn.commit()
            print(f"Data inserted into table '{table_name}'.")
        except Exception as e:
            print(f"Failed to insert data: {e}")
            self.conn.rollback()
            raise

    def get_daily_news(self, table_name: str, last_check_time: datetime):
        """
        新しく挿入されたレコードを取得
        :param table_name: テーブル名
        :param last_check_time: 最後にチェックした時間
        :return: 新しく挿入されたレコード
        """
        try:
            query = sql.SQL("SELECT * FROM {table} WHERE created_at > {last_check_time}").format(
                table=sql.Identifier(table_name),
                last_check_time=sql.Literal(last_check_time)
            )
            self.cursor.execute(query)
            column_names = [desc[0] for desc in self.cursor.description]
            new_records = [dict(zip(column_names, row)) for row in self.cursor.fetchall()]
            return new_records
        except Exception as e:
            print(f"Failed to retrieve new records: {e}")
            raise

    def fetch_all(self, table_name: str):
        """
        全てのデータを取得
        :param table_name: テーブル名
        :return: 取得したデータ
        """
        try:
            fetch_query = sql.SQL("SELECT * FROM {table}").format(
                table=sql.Identifier(table_name)
            )
            self.cursor.execute(fetch_query)
            rows = self.cursor.fetchall()
            print(f"Data fetched from table '{table_name}'.")
            return rows
        except Exception as e:
            print(f"Failed to fetch data: {e}")
            raise

    def update_news_content(self, news_id: int, content: str):
        """
        ニュース記事のコンテンツを更新
        :param news_id: ニュース記事のID
        :param content: 更新するコンテンツ
        """
        try:
            update_query = sql.SQL("UPDATE {table} SET content = %s WHERE id = %s").format(
                table=sql.Identifier("news")
            )
            self.cursor.execute(update_query, (content, news_id))
            self.conn.commit()
            print(f"ニュース記事 (ID: {news_id}) のコンテンツが更新されました。")
        except Exception as e:
            print(f"ニュース記事の更新に失敗しました: {e}")
            self.conn.rollback()
            raise

# if __name__ == "__main__":
#     # 環境変数からデータベースURLを取得
#     DATABASE_URL = os.getenv('DATABASE_URL')

#     # データベースクラスのインスタンス化
#     db = PostgresDatabase(DATABASE_URL)

#     # データベースに接続
#     db.connect()

#     # テーブル作成
#     db.create_table('articles', '''
#         id SERIAL PRIMARY KEY,
#         title VARCHAR(255) NOT NULL,
#         content TEXT NOT NULL,
#         summary TEXT,
#         published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#     ''')

#     # データ挿入
#     db.insert_data('articles', {
#         "title": "Example Title",
#         "content": "This is the content of the article.",
#         "summary": "This is a summary."
#     })

#     # データ取得
#     rows = db.fetch_all('articles')
#     for row in rows:
#         print(row)

#     # 接続を閉じる
#     db.close()
