from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage

def print_colored(text, color_code):
    print(f"\033[{color_code}m{text}\033[0m")

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

class Agent:

    def __init__(self, model, tools, system=""):
        self.system = system
        graph = StateGraph(AgentState)
        graph.add_node("llm", self.call_openai)
        graph.add_node("action", self.take_action)
        graph.add_conditional_edges(
            "llm",
            self.exists_action,
            {True: "action", False: END}
        )
        graph.add_edge("action", "llm")
        graph.set_entry_point("llm")
        self.graph = graph.compile()
        self.tools = {t.name: t for t in tools}
        self.model = model.bind_tools(tools)

    def exists_action(self, state: AgentState):
        result = state['messages'][-1]
        has_tools = len(result.tool_calls) > 0
        print_colored(f"Checking for tool calls: {has_tools}", "34")  # Blue
        if has_tools:
            print_colored(f"Tool calls found: {result.tool_calls}", "36")  # Cyan
        return has_tools

    def call_openai(self, state: AgentState,  message: str = None):
        messages = state['messages']
        if self.system:
            messages = [SystemMessage(content=self.system)] + messages
        print_colored("Sending request to OpenAI...", "34")  # Blue
        message = self.model.invoke(messages)
        print_colored(f"OpenAI response: {message}", "32")  # Green
        return {'messages': [message]}

    def take_action(self, state: AgentState):
        tool_calls = state['messages'][-1].tool_calls
        results = []
        for t in tool_calls:
            print_colored(f"Processing tool call: {t}", "36")  # Cyan
            print_colored(f"Available tools: {list(self.tools.keys())}", "34")  # Blue
            
            if not t['name'] in self.tools:
                print_colored(f"Invalid tool name: {t['name']}", "31")  # Red
                result = "bad tool name, retry"
            else:
                try:
                    print_colored(f"Executing {t['name']} with args: {t['args']}", "34")  # Blue
                    result = self.tools[t['name']](t['args'])
                    print_colored(f"Tool result: {result}", "32")  # Green
                except Exception as e:
                    print_colored(f"Tool execution error: {e}", "31")  # Red
                    result = f"Error executing {t['name']}: {str(e)}"
            
            results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))
        
        print_colored("Back to the model!", "33;1")  # Bold Yellow
        return {'messages': results}