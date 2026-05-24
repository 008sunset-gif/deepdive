"""Tavily Search API動作確認"""
import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

print("=== Tavily API テスト ===")
result = client.search(
    query="2026年 AIエージェント トレンド",
    search_depth="basic",
    max_results=3,
)

print(f"検索結果: {len(result['results'])} 件")
print()
for i, item in enumerate(result['results'], 1):
    print(f"--- 結果 {i} ---")
    print(f"タイトル: {item['title']}")
    print(f"URL: {item['url']}")
    print(f"内容（先頭150文字）: {item['content'][:150]}...")
    print()

print("=== 完了 ===")