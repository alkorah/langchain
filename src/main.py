import json
import os
 
import sys


 
from actions import call_awd, call_mainframe, call_db2
from agent import Agent

from langchain_openai import AzureChatOpenAI, AzureOpenAI
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage

from prompt import PROMPT_TEXT




tools =  [call_awd, call_mainframe,call_db2]

model = AzureChatOpenAI(
    deployment_name="gpt-4o-mini",
    model_name="gpt-4o-mini")

abot = Agent(model, tools, system=PROMPT_TEXT)

# Load payload from México.json
current_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(current_dir, 'payload', 'Canadian.json')

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)
    payload = json.dumps(data)

messages = [HumanMessage(content=payload)]
result = abot.graph.invoke({"messages": messages})    

 

print("Done")

print(result)


# Print all messages in the result in ascending order
for message in (result['messages']):
    print(message.content)


print (result['messages'][0].content)