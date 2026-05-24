"""
DeepDiveで使うデータスキーマ定義
各エージェント間のデータ受け渡しはこれらの構造化型を使う
"""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


# ===== Planner（計画立案）の出力 =====
class SubQuery(BaseModel):
    """個別の検索サブクエリ"""
    query: str = Field(description="Web検索に投げる具体的なクエリ文字列")
    intent: str = Field(description="このクエリで何を明らかにしたいか")
    priority: int = Field(default=2, ge=1, le=3, description="優先度: 1=高 2=中 3=低")


class ResearchPlan(BaseModel):
    """調査計画の全体像"""
    main_topic: str = Field(description="調査の主題（簡潔に）")
    sub_queries: List[SubQuery] = Field(description="3〜5個のサブクエリ")
    reasoning: str = Field(description="なぜこのサブクエリ群に分解したかの理由")


# ===== Researcher（情報収集）の出力 =====
class Source(BaseModel):
    """1つの情報源"""
    url: str
    title: str
    snippet: str = Field(description="関連箇所の抜粋")
    relevance: int = Field(default=3, ge=1, le=5, description="関連度: 1=低 5=高")


class Finding(BaseModel):
    """1つのサブクエリに対する調査結果"""
    sub_query: str
    sources: List[Source]
    summary: str = Field(description="このサブクエリで分かったことの要約")


# ===== Writer（レポート生成）の出力 =====
class ReportSection(BaseModel):
    """レポートの1セクション"""
    heading: str
    content: str
    cited_urls: List[str] = Field(default_factory=list)


class ResearchReport(BaseModel):
    """最終レポート"""
    title: str
    executive_summary: str = Field(description="3〜5文の要約")
    sections: List[ReportSection]
    references: List[str] = Field(description="参考URL一覧")
    markdown: str = Field(description="完成版のMarkdown形式レポート全文")


# ===== グラフ全体の状態 =====
class GraphState(BaseModel):
    """LangGraphのワークフロー全体で受け渡される状態"""
    # 入力
    user_question: str

    # Plannerの結果
    research_plan: Optional[ResearchPlan] = None

    # Researcherの結果
    findings: List[Finding] = Field(default_factory=list)

    # Writerの結果
    final_report: Optional[ResearchReport] = None

    # メタ情報
    status: Literal["planning", "researching", "writing", "done", "error"] = "planning"
    error_message: Optional[str] = None