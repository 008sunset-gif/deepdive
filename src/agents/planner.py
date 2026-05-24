"""
Planner Agent - 調査計画立案

ユーザーの質問を受けて、Web検索可能な3〜5個のサブクエリに分解する。
LLMの出力をPydanticスキーマで構造化することで、後続エージェントが
安全に扱える形に保証する。
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from src.schemas.models import ResearchPlan

load_dotenv()

# === LLM初期化 ===
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.3,
)

# 構造化出力をするLLM（Pydanticスキーマに従わせる）
planner_llm = llm.with_structured_output(ResearchPlan)

# === プロンプト ===
PLANNER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """あなたは優秀な調査計画立案者です。
ユーザーの質問を、Web検索で答えを集められる3〜5個の具体的なサブクエリに分解してください。

【サブクエリ作成の方針】
1. 各サブクエリは独立して検索可能であること
2. サブクエリ全体で、元の質問を多角的にカバーすること
3. 日本語と英語の検索を適切に混在させる（海外情報も必要なら英語クエリも入れる）
4. 各サブクエリには「この検索で何を明らかにしたいか」(intent) を明記
5. 優先度を付ける（1=最も重要、3=補足程度）

【出力】
ResearchPlan の構造で出力してください。"""),
    ("human", "{user_question}"),
])


def run_planner(user_question: str) -> ResearchPlan:
    """
    プランナーを実行する

    Args:
        user_question: ユーザーの調査依頼

    Returns:
        ResearchPlan: 構造化された調査計画
    """
    chain = PLANNER_PROMPT | planner_llm
    plan = chain.invoke({"user_question": user_question})
    return plan


# === 動作確認 ===
if __name__ == "__main__":
    test_question = "2026年の製造業AIエージェント活用事例について調べたい"

    print("=" * 60)
    print(f"質問: {test_question}")
    print("=" * 60)
    print()

    plan = run_planner(test_question)

    print(f"📋 主題: {plan.main_topic}")
    print(f"💡 計画理由: {plan.reasoning}")
    print()
    print(f"🔍 サブクエリ ({len(plan.sub_queries)}個):")
    for i, sq in enumerate(plan.sub_queries, 1):
        print(f"\n  {i}. [優先度{sq.priority}] {sq.query}")
        print(f"     狙い: {sq.intent}")

    print()
    print("--- JSON ---")
    print(plan.model_dump_json(indent=2))