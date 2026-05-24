"""スキーマ動作確認"""
from src.schemas.models import (
    SubQuery,
    ResearchPlan,
    Source,
    Finding,
    GraphState,
)

# サブクエリを作る
q1 = SubQuery(
    query="LangGraph マルチエージェント 2026",
    intent="LangGraphによる最新のマルチエージェント実装パターンを知る",
    priority=1,
)

q2 = SubQuery(
    query="AI agent framework comparison 2026",
    intent="主要エージェントフレームワークの比較",
    priority=2,
)

# 計画を作る
plan = ResearchPlan(
    main_topic="LangGraphを使ったAIエージェント開発",
    sub_queries=[q1, q2],
    reasoning="日本語と英語の両方の最新情報が必要",
)

# 状態を作る
state = GraphState(
    user_question="LangGraphでAIエージェントを作るには?",
    research_plan=plan,
)

print("=== スキーマテスト ===")
print(f"質問: {state.user_question}")
print(f"主題: {state.research_plan.main_topic}")
print(f"サブクエリ数: {len(state.research_plan.sub_queries)}")
print()
print("サブクエリ一覧:")
for i, sq in enumerate(state.research_plan.sub_queries, 1):
    print(f"  {i}. [優先度{sq.priority}] {sq.query}")
    print(f"     狙い: {sq.intent}")

print()
print("--- JSON出力（構造化出力のサンプル）---")
print(state.model_dump_json(indent=2))
print("=== 完了 ===")