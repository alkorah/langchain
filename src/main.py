import json
import os
import sys

from actions import call_awd, call_mainframe, call_db2, call_agent_dataSource
from agent import Agent
from langchain_openai import AzureChatOpenAI, AzureOpenAI
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage
from prompt import PROMPT_TEXT
from swagger_processor import SwaggerProcessor

tools = [call_awd, call_mainframe, call_db2, call_agent_dataSource]

model = AzureChatOpenAI(
    deployment_name="gpt-4o-mini",
    model_name="gpt-4o-mini")

abot = Agent(model, tools, system=PROMPT_TEXT)

# Load payload from México.json
with open('src/payload/Canadian.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    payload = json.dumps(data)

messages = [HumanMessage(content=payload)]
result = abot.graph.invoke({"messages": messages})    

print("Done")
print(result)

# Print all messages in the result in ascending order
for message in (result['messages']):
    print(message.content)

print(result['messages'][0].content)

# Get Swagger details from swaggerneedfix.json file
# with open('src/swaggerneedfix.json', 'r', encoding='utf-8') as f:
#     swagger_spec = json.load(f)

# processor = SwaggerProcessor(swagger_spec)
# extracted_info = processor.extract_information()
# formatted_info = processor.format_for_llm(extracted_info)
# print(formatted_info)
