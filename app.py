"""
DeepDive - Streamlit UI

ブラウザで動く対話型インターフェース。
ユーザーの質問を受けて、エージェントが調査レポートを生成する過程を
リアルタイムで可視化する。
"""

import streamlit as st
from src.schemas.models import GraphState
from src.agents.planner import run_planner
from src.agents.researcher import run_researcher
from src.agents.writer import run_writer

# ===== ページ設定 =====
st.set_page_config(
    page_title="DeepDive - AI調査エージェント",
    page_icon="🔬",
    layout="wide",
)

# ===== セッション状態の初期化 =====
if "history" not in st.session_state:
    st.session_state.history = []

if "current_result" not in st.session_state:
    st.session_state.current_result = None

# ===== サイドバー =====
with st.sidebar:
    st.title("🔬 DeepDive")
    st.caption("AI調査エージェント")

    st.divider()

    st.markdown("### 💡 このアプリについて")
    st.markdown(
        """
        4つのAIエージェントが連携して、Web検索を繰り返しながら
        調査レポートを自動生成します。

        **エージェント構成**
        1. 📋 Planner - 計画立案
        2. 🔍 Researcher - 情報収集
        3. ✍️ Writer - レポート統合

        ※ v0.2 で Evaluator（自己批評）追加予定
        """
    )

    st.divider()

    st.markdown("### 🛠️ 技術スタック")
    st.markdown(
        """
        - LangGraph
        - LangChain
        - Gemini 2.5 Flash-Lite
        - Tavily Search API
        - Pydantic
        - Streamlit
        """
    )

    st.divider()

    # 履歴
    if st.session_state.history:
        st.markdown("### 📚 調査履歴")
        for i, item in enumerate(reversed(st.session_state.history[-5:])):
            with st.expander(f"{item['question'][:30]}..."):
                st.markdown(f"**質問**: {item['question']}")
                st.markdown(f"**タイトル**: {item['title']}")
                if st.button(f"このレポートを表示", key=f"hist_{i}"):
                    st.session_state.current_result = item['result']
                    st.rerun()

# ===== メインエリア =====
st.title("🔬 DeepDive")
st.markdown("**マルチエージェントAIによる自律調査システム**")
st.markdown(
    "質問を入力すると、AIエージェントが自律的にWeb検索を繰り返し、"
    "調査レポートを生成します。"
)

st.divider()

# ===== 質問入力フォーム =====
with st.container():
    st.markdown("### 💬 調査したいことを入力")

    # サンプル質問
    sample_questions = [
        "2026年の生成AI活用事例を業種別に調べたい",
        "LangGraphとCrewAIの違いを比較したい",
        "AIエージェントの最新トレンドを知りたい",
        "RAGシステムの実装パターンを調べたい",
    ]

    st.markdown("**💡 サンプル質問**")
    sample_cols = st.columns(2)
    for i, sample in enumerate(sample_questions):
        if sample_cols[i % 2].button(sample, use_container_width=True, key=f"sample_{i}"):
            st.session_state.current_question = sample

    question = st.text_area(
        "質問内容",
        value=st.session_state.get("current_question", ""),
        placeholder="例: 2026年の製造業AIエージェント活用事例を調べたい",
        height=100,
        label_visibility="collapsed",
    )

    submit = st.button("🚀 調査を開始", type="primary", use_container_width=True)

# ===== 実行 =====
if submit and question.strip():
    # ログエリア
    log_container = st.container()
    progress_bar = st.progress(0, "準備中...")

    try:
        with log_container:
            st.markdown("### 🤖 エージェント実行ログ")

            # ===== Step 1: Planner =====
            with st.status("📋 [Planner] 調査計画を立案中...", expanded=True) as status:
                progress_bar.progress(10, "Planner実行中...")
                plan = run_planner(question)
                st.success(f"✓ {len(plan.sub_queries)} 個のサブクエリを生成しました")

                st.markdown("**生成されたサブクエリ:**")
                for i, sq in enumerate(plan.sub_queries, 1):
                    st.markdown(f"- **{i}. [優先度{sq.priority}]** {sq.query}")
                    st.caption(f"  狙い: {sq.intent}")

                status.update(label="📋 [Planner] 計画立案完了", state="complete")

            progress_bar.progress(25, "Researcher実行中...")

            # ===== Step 2: Researcher =====
            with st.status("🔍 [Researcher] Web検索による情報収集中...", expanded=True) as status:
                findings = run_researcher(plan.sub_queries)

                for f in findings:
                    st.success(f"✓ 「{f.sub_query}」: {len(f.sources)} 件取得")

                status.update(label=f"🔍 [Researcher] {len(findings)} 件の調査完了", state="complete")

            progress_bar.progress(75, "Writer実行中...")

            # ===== Step 3: Writer =====
            with st.status("✍️ [Writer] レポート統合中...", expanded=True) as status:
                report = run_writer(question, plan, findings)
                st.success(f"✓ レポート完成: {report.title}")
                status.update(label="✍️ [Writer] レポート生成完了", state="complete")

            progress_bar.progress(100, "完了!")

            # ===== 結果保存 =====
            result = GraphState(
                user_question=question,
                research_plan=plan,
                findings=findings,
                final_report=report,
                status="done",
            )
            st.session_state.current_result = result
            st.session_state.history.append({
                "question": question,
                "title": report.title,
                "result": result,
            })

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")

# ===== 結果表示 =====
if st.session_state.current_result is not None:
    result = st.session_state.current_result

    st.divider()
    st.markdown("## 📄 調査レポート")

    # メタ情報
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📋 サブクエリ", len(result.research_plan.sub_queries))
    col2.metric("🔍 情報源", sum(len(f.sources) for f in result.findings))
    col3.metric("📑 セクション", len(result.final_report.sections))
    col4.metric("📚 参考文献", len(result.final_report.references))

    st.divider()

    # レポート本文
    st.markdown(result.final_report.markdown)

    st.divider()

    # ダウンロード
    st.download_button(
        label="💾 レポートをダウンロード (Markdown)",
        data=result.final_report.markdown,
        file_name=f"{result.final_report.title}.md",
        mime="text/markdown",
        use_container_width=True,
    )

    # 詳細情報
    with st.expander("🔍 調査の詳細（デバッグ情報）"):
        st.markdown("### 調査計画")
        st.json(result.research_plan.model_dump())

        st.markdown("### 調査結果（要約のみ）")
        for f in result.findings:
            st.markdown(f"**{f.sub_query}**")
            st.markdown(f.summary)
            st.markdown("---")

# ===== フッター =====
st.divider()
st.caption("DeepDive v0.1 | Powered by LangGraph + Gemini + Tavily")