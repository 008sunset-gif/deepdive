"""Gemini API動作確認"""
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.2,
)

print("=== Gemini API テスト ===")
response = llm.invoke("こんにちは、自己紹介してください")
print(response.content)
print("=== 完了 ===")