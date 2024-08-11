import requests

class GetNewsBing:
    def __init__(self, subscription_key, market="ja-JP"):
        """
        コンストラクタ: NewsFetcher クラスのインスタンスを初期化
        :param subscription_key: Bing News Search APIのサブスクリプションキー
        :param market: 市場情報（デフォルトは "ja-JP"）
        """
        self.subscription_key = "c0057c9bf908401c859e09fd8b08b7fe"
        self.market = market
        self.search_url = "https://api.bing.microsoft.com/v7.0/news"
        self.headers = {"Ocp-Apim-Subscription-Key": self.subscription_key}
    
    def get_customized_top_news(self, category=None, count=5, freshness="Day"):
        """
        カスタマイズされたトップニュースを取得
        :param category: ニュースカテゴリー
        :param count: 取得するニュースの数
        :param freshness: ニュースの鮮度（デフォルトは "Day"）
        :return: ニュース結果のリスト
        """
        params = {
            "category": category,
            "count": count,
            "mkt": self.market,
            "freshness": freshness,
            "sortBy": "Relevance",
            "textFormat": "Raw"
        }
        
        response = requests.get(self.search_url, headers=self.headers, params=params)
        response.raise_for_status()
        news_results = response.json()
        
        return news_results["value"]

# 使用例

# if __name__ == "__main__":
#     # サブスクリプションキーを設定
#     subscription_key = "c0057c9bf908401c859e09fd8b08b7fe"
    
#     # NewsFetcherクラスのインスタンスを作成
#     news_fetcher = NewsFetcher(subscription_key)
    
#     # カスタマイズされたトップニュースを取得
#     top_news = news_fetcher.get_customized_top_news(category="Technology", count=5)
    
#     # 結果を表示
#     for news in top_news:
#         print(news["name"])
#         print(news["url"])
#         print()
