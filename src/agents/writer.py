"""
Writer Agent - レポート生成

Researcherがまとめた複数の Finding を統合し、
Markdown形式の調査レポートを生成する。
ユーザーの元の質問に答える形で論理的に構成する。
"""

import os
from typing import List
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from src.schemas.models import (
    ResearchPlan,
    Finding,
    ResearchReport,
    ReportSection,
)

load_dotenv()

# === LLM初期化 ===
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.3,
)

# 構造化出力のLLM
writer_llm = llm.with_structured_output(ResearchReport)


# === プロンプト ===
SYSTEM_INSTRUCTION = """あなたは優秀なリサーチライターです。
複数の調査結果を統合し、ユーザーの質問に答える調査レポートを書いてください。

【ルール】
1. 調査結果に書かれた内容のみを根拠とする（推測・一般論で補完しない）
2. 重要な数字、固有名詞、事例は必ず含める
3. 論理的な構成にする（概要 → 詳細 → 示唆）
4. 各セクションの主張には、根拠となるURLを明記する
5. 情報源同士で矛盾がある場合は両論併記する
6. レポートは Markdown 形式で書く

【Markdown構造の指針】
- 最初に「# タイトル」
- その下に「## エグゼクティブサマリー」で3〜5文の要約
- 続いて「## 1. xxx」「## 2. xxx」のようにセクションを並べる
- 各主張の後に「> 出典: [タイトル](URL)」を入れる
- 最後に「## まとめ」と「## 参考文献」を入れる

【出力】
ResearchReport の構造で出力してください。
特に markdown フィールドには完成版Markdown全文を入れてください。"""

USER_TEMPLATE = """【ユーザーの質問】
{user_question}

【調査計画】
主題: {main_topic}
立案理由: {reasoning}

【調査結果】
{findings_text}

【出力】
上記の調査結果を統合して、ユーザーの質問に答える調査レポートを作成してください。"""

WRITER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_INSTRUCTION),
    ("human", USER_TEMPLATE),
])


def format_findings_for_llm(findings: List[Finding]) -> str:
    """調査結果一覧をLLMが読みやすい形式に整形"""
    if not findings:
        return "（調査結果なし）"

    formatted = []
    for i, f in enumerate(findings, 1):
        formatted.append(f"### 調査{i}: {f.sub_query}\n")
        formatted.append(f"【要約】\n{f.summary}\n")
        formatted.append("【情報源】")
        for src in f.sources:
            formatted.append(
                f"- [{src.title}]({src.url}) (関連度{src.relevance}/5)\n"
                f"  抜粋: {src.snippet[:300]}..."
            )
        formatted.append("\n" + "-" * 40 + "\n")

    return "\n".join(formatted)


def run_writer(
    user_question: str,
    research_plan: ResearchPlan,
    findings: List[Finding],
) -> ResearchReport:
    """
    最終レポートを生成する

    Args:
        user_question: ユーザーの元の質問
        research_plan: Plannerが立てた計画
        findings: Researcherがまとめた調査結果

    Returns:
        ResearchReport: 完成版レポート
    """
    findings_text = format_findings_for_llm(findings)

    chain = WRITER_PROMPT | writer_llm
    report = chain.invoke({
        "user_question": user_question,
        "main_topic": research_plan.main_topic,
        "reasoning": research_plan.reasoning,
        "findings_text": findings_text,
    })

    return report


# === 動作確認 ===
if __name__ == "__main__":
    from src.agents.planner import run_planner
    from src.agents.researcher import run_researcher

    test_question = "2026年のAIエージェント実装方法とフレームワーク選定のポイントを調べたい"

    print("=" * 60)
    print(f"質問: {test_question}")
    print("=" * 60)
    print()

    # Step 1: Planner
    print("📋 Step 1: Planner 実行中...")
    plan = run_planner(test_question)
    print(f"   → {len(plan.sub_queries)} 個のサブクエリを生成")
    print()

    # Step 2: Researcher
    print("🔍 Step 2: Researcher 実行中...")
    findings = run_researcher(plan.sub_queries)
    print(f"   → {len(findings)} 件の調査結果を生成")
    print()

    # Step 3: Writer
    print("✍️  Step 3: Writer 実行中...")
    report = run_writer(test_question, plan, findings)
    print("   → レポート完成")
    print()

    # 結果表示
    print("=" * 60)
    print("最終レポート")
    print("=" * 60)
    print()
    print(report.markdown)
    print()
    print("=" * 60)
    print(f"タイトル: {report.title}")
    print(f"セクション数: {len(report.sections)}")
    print(f"参考文献数: {len(report.references)}")
    print("=" * 60)