#  DeepDive - マルチエージェント型AI調査エージェント

質問を入力するだけで、4つのAIエージェントが自律的にWeb検索と情報統合を繰り返し、Markdown形式の調査レポートを自動生成するアプリケーションです。

LangGraphによる状態遷移ベースのオーケストレーションと、Pydanticによる構造化出力を組み合わせ、2026年のAIエージェント開発のベストプラクティスに沿って実装しました。

---

##  特徴

-  **マルチエージェント構成**：Planner → Researcher → Writer の3エージェントが連携
-  **構造化出力**：各エージェントの出力を Pydantic で型保証
-  **Tool Use**：Tavily Search API による Web 検索ツール統合
-  **引用付きレポート**：すべての主張に出典 URL を明記
-  **ローカル完結**：自分の API キーで自分の PC で動作（クラウドサーバー経由なし）
-  **Markdown ダウンロード**：生成レポートを即座にローカル保存

---

##  アーキテクチャ

ユーザーの質問は LangGraph の StateGraph 内を以下の順で流れます。

1. ** Planner** - 質問を 3〜5 個のサブクエリに分解（出力: ResearchPlan）
2. ** Researcher** - 各サブクエリを Tavily Search API で並列検索し、結果を要約（出力: List[Finding]）
3. ** Writer** - 全調査結果を統合して Markdown レポートを生成（出力: ResearchReport）

各エージェントは LangGraph のノードとして実装され、GraphState を介して状態を受け渡します。

---

##  技術スタック

| 領域 | 採用技術 |
|------|----------|
| 言語 | Python 3.12 |
| LLM | Google Gemini 2.5 Flash Lite |
| エージェント基盤 | LangGraph |
| LLM ラッパー | LangChain |
| Web 検索 | Tavily Search API |
| 構造化出力 | Pydantic |
| UI | Streamlit |

---

##  セットアップ

### 必要なもの

- Python 3.12 以上
- Google Gemini API キー（無料取得: https://aistudio.google.com）
- Tavily Search API キー（無料取得: https://tavily.com）

### インストール手順

1. リポジトリをクローン
2. 仮想環境を作成して有効化
3. requirements.txt から依存パッケージをインストール
4. .env.example を .env にコピーして、自分の API キーを記入
5. `streamlit run app.py` で起動

詳しいコマンドは末尾の付録を参照してください。

---

##  使い方

1. ブラウザで起動した DeepDive を開く
2. サンプル質問をクリック、または自分の質問を入力
3. 「調査を開始」を押す
4. 4つのエージェントが自律的に動く様子をリアルタイムで観察
5. 完成したレポートを画面で確認
6. 「レポートをダウンロード」で Markdown ファイルとして保存

---

## プロジェクト構成

- `app.py` - Streamlit UI のエントリーポイント
- `requirements.txt` - 依存パッケージ一覧
- `.env.example` - 環境変数の雛形（API キーは利用者が記入）
- `README.md` - 本ファイル
- `src/agents/` - 各エージェントの実装
  - `planner.py` - 計画立案エージェント
  - `researcher.py` - 情報収集エージェント
  - `writer.py` - レポート生成エージェント
- `src/tools/` - 外部 API 統合
  - `web_search.py` - Tavily API ラッパー
- `src/graph/` - LangGraph ワークフロー
  - `workflow.py` - StateGraph 定義
- `src/schemas/` - データスキーマ
  - `models.py` - Pydantic モデル定義
- `test_*.py` - 各コンポーネントの単体テスト

---

## 設計上の工夫

### 1. 構造化出力による型保証
各エージェントの出力を Pydantic スキーマ（ResearchPlan、Finding、ResearchReport）で定義し、`with_structured_output` で LLM の出力を強制変換しています。これにより後続エージェントが「型が違ってエラー」になることを防ぎます。

### 2. ハルシネーション対策
Writer エージェントには「調査結果に書かれた内容のみを根拠にする」「主張には引用元 URL を明記する」というルールをプロンプトに組み込み、各セクション末尾に出典を必ず含める設計にしています。

### 3. ローカル完結
個人情報を含む調査ログを外部サービスに残さないよう、利用者が自分の API キーで自分の PC で動かす構成にしています。クラウドへのデプロイは行わず、GitHub でコード公開のみの形式を取っています。

### 4. レート制限を考慮したモデル選定
Google Gemini の無料枠制約下で動作するよう、gemini-2.5-flash-lite（1日1,000リクエスト無料枠）を採用しています。

---

## ロードマップ

- [x] **v0.1** - 3エージェント連携の基本構成、Streamlit UI、GitHub 公開
- [ ] **v0.2** - 自己批評ループ（Evaluator エージェント追加、情報不足時の追加調査）
- [ ] **v0.3** - PDF 文書をアップロード可能に（ローカル文書も調査ソースに）
- [ ] **v1.0** - 調査履歴のベクトル検索、Markdown 以外の出力形式対応

---

## 制約

- **Gemini 無料枠**：1日のリクエスト数に上限あり。多用すると 429 エラー（レート制限）になります
- **Tavily 無料枠**：月1,000リクエストまで
- **言語**：日本語と英語に最適化（他言語は精度未検証）
- **検索深度**：v0.1 は単一パス（1回検索して終わり）。v0.2 で深掘りループを追加予定

---

## ライセンス

MIT License

---

## 作者

大場 祐飛 (Yuhi Oba)

このプロジェクトは、2026年の AI エージェント開発トレンドを学習する目的で個人開発したものです。LangGraph、構造化出力、Tool Use、マルチエージェントオーケストレーション等を実装するハンズオン教材としても活用できます。

---

## 付録：詳細なセットアップコマンド

リポジトリをクローン:

    git clone https://github.com/008sunset-gif/deepdive.git
    cd deepdive

仮想環境を作成・有効化 (Windows):

    python -m venv .venv
    .venv\Scripts\activate

仮想環境を作成・有効化 (macOS / Linux):

    python -m venv .venv
    source .venv/bin/activate

依存パッケージのインストール:

    pip install -r requirements.txt

環境変数の設定:

    cp .env.example .env
    # .env を編集して、自分の API キーを記入

起動:

    streamlit run app.py

ブラウザで http://localhost:8501 が自動的に開きます。
