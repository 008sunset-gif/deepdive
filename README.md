各エージェントは LangGraph のノードとして実装され、`GraphState` を介して状態を受け渡します。

---

## 🛠️ 技術スタック

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

## 📦 セットアップ

### 必要なもの
- Python 3.12 以上
- Google Gemini API キー（[無料取得](https://aistudio.google.com)）
- Tavily Search API キー（[無料取得](https://tavily.com)、月1,000リクエストまで無料）

### インストール手順

```bash
# 1. リポジトリをクローン
git clone https://github.com/Yuhi-Oba/deepdive.git
cd deepdive

# 2. 仮想環境を作成・有効化
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# 3. 依存パッケージのインストール
pip install -r requirements.txt

# 4. 環境変数の設定
cp .env.example .env
# .env を編集して、自分の API キーを記入

# 5. 起動
streamlit run app.py
```

ブラウザで `http://localhost:8501` が自動的に開きます。

---

## 🚀 使い方

1. ブラウザで起動した DeepDive を開く
2. サンプル質問をクリック、または自分の質問を入力
3. 「🚀 調査を開始」を押す
4. 4つのエージェントが自律的に動く様子をリアルタイムで観察
5. 完成したレポートを画面で確認
6. 「💾 レポートをダウンロード」で Markdown ファイルとして保存

---

## 📂 プロジェクト構成