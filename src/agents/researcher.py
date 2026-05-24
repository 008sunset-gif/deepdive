"""
Researcher Agent - 情報収集

Plannerが作った各サブクエリに対してWeb検索を実行し、
取得した情報を構造化された Finding として返す。
各サブクエリの結果を LLM に要約させ、後続の Writer が使いやすい形にする。
"""

import os
from typing import List
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.schemas.models import SubQuery, Source, Finding
from src.tools.web_search import search_web

load_dotenv()

# === LLM初期化 ===
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.2,
)

# === 要約用プロンプト ===
SUMMARIZER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """あなたは優秀な情報分析者です。
あるサブクエリに対する複数のWeb検索結果を読み、
そのサブクエリが知りたかったことに対する答えを簡潔にまとめてください。

【ルール】
1. 検索結果に書かれていることだけを根拠にする
2. 推測や一般論で補完しない
3. 重要な数字、固有名詞、事例があれば必ず含める
4. 5〜10文程度の要約にまとめる
5. 情報が不足している場合は「情報が不足している」と明記する

【出力】
要約テキストのみを出力してください。"""),
    ("human", """【サブクエリ】
{query}

【知りたかったこと】
{intent}

【検索結果】
{sources_text}

【要約】""")
])

summarizer_chain = SUMMARIZER_PROMPT | llm | StrOutputParser()


def format_sources_for_llm(sources: List[Source]) -> str:
    """検索結果をLLMが読みやすい形式に整形"""
    if not sources:
        return "（検索結果なし）"

    formatted = []
    for i, src in enumerate(sources, 1):
        formatted.append(
            f"--- 情報源 {i} (関連度 {src.relevance}/5) ---\n"
            f"タイトル: {src.title}\n"
            f"URL: {src.url}\n"
            f"内容: {src.snippet}\n"
        )
    return "\n".join(formatted)


def research_one_query(sub_query: SubQuery, max_results: int = 4) -> Finding:
    """
    1つのサブクエリに対して検索 + 要約を実行

    Args:
        sub_query: 検索するサブクエリ
        max_results: 検索結果の最大件数

    Returns:
        Finding: このサブクエリに対する調査結果
    """
    print(f"  🔍 検索中: {sub_query.query}")

    # Step 1: Web検索
    sources = search_web(sub_query.query, max_results=max_results)
    print(f"     → {len(sources)} 件取得")

    # Step 2: LLMで要約
    if sources:
        sources_text = format_sources_for_llm(sources)
        summary = summarizer_chain.invoke({
            "query": sub_query.query,
            "intent": sub_query.intent,
            "sources_text": sources_text,
        })
    else:
        summary = "（検索結果なし、情報が取得できませんでした）"

    return Finding(
        sub_query=sub_query.query,
        sources=sources,
        summary=summary,
    )


def run_researcher(sub_queries: List[SubQuery]) -> List[Finding]:
    """
    すべてのサブクエリに対して調査を実行

    Args:
        sub_queries: 調査対象のサブクエリリスト

    Returns:
        List[Finding]: 各サブクエリに対する調査結果のリスト
    """
    findings = []
    for i, sq in enumerate(sub_queries, 1):
        print(f"\n[{i}/{len(sub_queries)}] サブクエリ調査中")
        finding = research_one_query(sq)
        findings.append(finding)
    return findings


# === 動作確認 ===
if __name__ == "__main__":
    # テスト用のサブクエリを2つ作る
    test_queries = [
        SubQuery(
            query="LangGraph マルチエージェント 実装方法",
            intent="LangGraphを使ったマルチエージェント実装の手順を知る",
            priority=1,
        ),
        SubQuery(
            query="AI agent framework 2026 comparison",
            intent="2026年の主要AIエージェントフレームワーク比較",
            priority=2,
        ),
    ]

    print("=" * 60)
    print("Researcher エージェント テスト")
    print("=" * 60)

    findings = run_researcher(test_queries)

    print("\n" + "=" * 60)
    print("調査結果サマリー")
    print("=" * 60)

    for i, finding in enumerate(findings, 1):
        print(f"\n【{i}. {finding.sub_query}】")
        print(f"取得情報源: {len(finding.sources)} 件")
        print(f"\n要約:\n{finding.summary}")
        print()
        print("情報源URL:")
        for src in finding.sources:
            print(f"  - [{src.relevance}/5] {src.url}")
        print()
        print("-" * 60)