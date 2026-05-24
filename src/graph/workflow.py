"""
DeepDive Workflow - LangGraphによるエージェントオーケストレーション

3つのエージェント（Planner → Researcher → Writer）を
LangGraphのStateGraphとして接続し、状態遷移を管理する。

このグラフは将来的に:
- Evaluatorによる自己批評ループ
- 条件分岐（情報不足時の再検索）
- 並列実行（複数サブクエリの同時調査）
などに拡張可能な構造で設計されている。
"""

from typing import Literal
from langgraph.graph import StateGraph, START, END

from src.schemas.models import GraphState
from src.agents.planner import run_planner
from src.agents.researcher import run_researcher
from src.agents.writer import run_writer


# === 各ノード関数 ===
# 各ノードはGraphStateを受け取り、更新したGraphStateを返す

def planning_node(state: GraphState) -> GraphState:
    """調査計画立案ノード"""
    print("\n📋 [Planner] 調査計画を立案中...")
    plan = run_planner(state.user_question)
    print(f"   → {len(plan.sub_queries)} 個のサブクエリを生成")

    # 状態を更新
    return state.model_copy(update={
        "research_plan": plan,
        "status": "researching",
    })


def researching_node(state: GraphState) -> GraphState:
    """情報収集ノード"""
    print("\n🔍 [Researcher] 情報収集を開始...")
    findings = run_researcher(state.research_plan.sub_queries)
    print(f"   → {len(findings)} 件の調査結果を生成")

    return state.model_copy(update={
        "findings": findings,
        "status": "writing",
    })


def writing_node(state: GraphState) -> GraphState:
    """レポート生成ノード"""
    print("\n✍️  [Writer] レポート生成中...")
    report = run_writer(
        user_question=state.user_question,
        research_plan=state.research_plan,
        findings=state.findings,
    )
    print("   → レポート完成")

    return state.model_copy(update={
        "final_report": report,
        "status": "done",
    })


# === グラフ構築 ===
def build_graph():
    """DeepDiveのワークフローグラフを構築"""
    workflow = StateGraph(GraphState)

    # ノードを追加
    workflow.add_node("planner", planning_node)
    workflow.add_node("researcher", researching_node)
    workflow.add_node("writer", writing_node)

    # エッジを定義（START → planner → researcher → writer → END）
    workflow.add_edge(START, "planner")
    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "writer")
    workflow.add_edge("writer", END)

    return workflow.compile()


# === メインエントリ ===
def run_deepdive(user_question: str) -> GraphState:
    """
    DeepDiveを実行する

    Args:
        user_question: ユーザーの調査依頼

    Returns:
        GraphState: 全ての結果を含む最終状態
    """
    graph = build_graph()

    initial_state = GraphState(user_question=user_question)
    final_state = graph.invoke(initial_state)

    # LangGraphはdict形式で返してくるのでGraphStateに戻す
    if isinstance(final_state, dict):
        final_state = GraphState(**final_state)

    return final_state


# === 動作確認 ===
if __name__ == "__main__":
    test_question = "2026年の生成AIによる業務効率化の最新事例を調べたい"

    print("=" * 60)
    print("DeepDive ワークフロー実行")
    print("=" * 60)
    print(f"質問: {test_question}")
    print("=" * 60)

    final_state = run_deepdive(test_question)

    print()
    print("=" * 60)
    print("📄 最終レポート")
    print("=" * 60)
    print()
    print(final_state.final_report.markdown)

    print()
    print("=" * 60)
    print("📊 ワークフロー統計")
    print("=" * 60)
    print(f"ステータス: {final_state.status}")
    print(f"サブクエリ数: {len(final_state.research_plan.sub_queries)}")
    print(f"調査件数: {len(final_state.findings)}")
    print(f"レポートタイトル: {final_state.final_report.title}")
    print(f"セクション数: {len(final_state.final_report.sections)}")
    print(f"参考文献数: {len(final_state.final_report.references)}")
    print("=" * 60)