"""
Web Search Tool - Tavily APIラッパー

Tavily Search APIを呼び出し、結果をSource構造体のリストに変換する。
Researcherエージェントから呼ばれる。
"""

import os
from typing import List
from dotenv import load_dotenv
from tavily import TavilyClient

from src.schemas.models import Source

load_dotenv()

# === Tavilyクライアント初期化 ===
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def search_web(query: str, max_results: int = 5) -> List[Source]:
    """
    Web検索を実行し、結果をSourceのリストとして返す

    Args:
        query: 検索クエリ
        max_results: 取得する最大件数

    Returns:
        List[Source]: 検索結果のリスト
    """
    try:
        result = tavily_client.search(
            query=query,
            search_depth="advanced",  # advancedの方が品質高い
            max_results=max_results,
        )

        sources = []
        for item in result.get("results", []):
            # Tavilyのscoreは0〜1の浮動小数。1〜5の整数relevanceに変換
            tavily_score = item.get("score", 0.5)
            relevance = max(1, min(5, round(tavily_score * 5)))

            source = Source(
                url=item.get("url", ""),
                title=item.get("title", "（タイトル不明）"),
                snippet=item.get("content", "")[:500],  # 先頭500文字
                relevance=relevance,
            )
            sources.append(source)

        return sources

    except Exception as e:
        print(f"⚠️ Web検索エラー: {e}")
        return []


# === 動作確認 ===
if __name__ == "__main__":
    test_query = "LangGraph マルチエージェント 2026"

    print("=" * 60)
    print(f"検索クエリ: {test_query}")
    print("=" * 60)
    print()

    sources = search_web(test_query, max_results=3)

    print(f"取得件数: {len(sources)}")
    print()

    for i, src in enumerate(sources, 1):
        print(f"--- 結果 {i} (関連度 {src.relevance}/5) ---")
        print(f"タイトル: {src.title}")
        print(f"URL: {src.url}")
        print(f"抜粋: {src.snippet[:200]}...")
        print()