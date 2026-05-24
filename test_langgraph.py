"""LangGraph動作確認（最小サンプル）"""
from typing import TypedDict
from langgraph.graph import StateGraph, END


class State(TypedDict):
    counter: int
    message: str


def node_a(state: State) -> State:
    print(f"[Node A] 受け取った値: counter={state['counter']}")
    return {"counter": state['counter'] + 1, "message": "Aを通過"}


def node_b(state: State) -> State:
    print(f"[Node B] 受け取った値: counter={state['counter']}, message={state['message']}")
    return {"counter": state['counter'] + 10, "message": "Bを通過"}


workflow = StateGraph(State)
workflow.add_node("a", node_a)
workflow.add_node("b", node_b)
workflow.set_entry_point("a")
workflow.add_edge("a", "b")
workflow.add_edge("b", END)

app = workflow.compile()

print("=== LangGraph テスト ===")
result = app.invoke({"counter": 0, "message": ""})
print(f"\n最終結果: {result}")
print("=== 完了 ===")