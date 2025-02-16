from azure.storage.queue import QueueServiceClient
import os
from dotenv import load_dotenv
from langchain_core.tools import tool
import requests
from agent import Agent
from langchain_openai import AzureChatOpenAI
from prompt_DMO import PROMPT_DMO
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage

# Load environment variables from .env file
load_dotenv()

# Initialize the QueueServiceClient
queue_service_client = QueueServiceClient.from_connection_string(os.getenv("AZURE_STORAGE_CONNECTION_STRING"))

def print_colored(text, color_code):
    print(f"\033[{color_code}m{text}\033[0m")

@tool
def call_mainframe(payload: str, queue_name: str = "intake-queue"):
    """
    Send a message to the mainframe queue.

    Args:
        payload (str): The message payload to send.
        queue_name (str): The name of the queue to send the message to.

    Returns:
        str: A message indicating the result of the operation.
    """
    queue_client = queue_service_client.get_queue_client(queue_name)
    try:
        print_colored(f"payload is {payload}", "36")  # Cyan
        response = queue_client.send_message(payload)
        print_colored(f"Payload inserted into the {queue_name} queue successfully.", "32")  # Green
        print_colored(f"Message ID: {response.id}, Insertion Time: {response.inserted_on}", "32")  # Green
        return f"Message has been inserted into the {queue_name} queue successfully."
    except Exception as e:
        print_colored(f"Failed to insert payload into the {queue_name} queue.", "31")  # Red
        print_colored(f"Error: {e}", "31")  # Red
        return f"Failed to insert message into the {queue_name} queue."

@tool
def call_awd(payload: str, queue_name: str = "intake-queue"):
    """
    Send a message to the AWD queue.

    Args:
        payload (str): The message payload to send.
        queue_name (str): The name of the queue to send the message to.

    Returns:
        str: A message indicating the result of the operation.
    """
    queue_client = queue_service_client.get_queue_client(queue_name)
    try:
        print_colored(f"payload is {payload}", "36")  # Cyan
        response = queue_client.send_message(payload)
        print_colored(f"Payload inserted into the {queue_name} queue successfully.", "32")  # Green
        print_colored(f"Message ID: {response.id}, Insertion Time: {response.inserted_on}", "32")  # Green
        return f"Message has been inserted into the {queue_name} queue successfully."
    except Exception as e:
        print_colored(f"Failed to insert payload into the {queue_name} queue.", "31")  # Red
        print_colored(f"Error: {e}", "31")  # Red
        return f"Failed to insert message into the {queue_name} queue."
    
@tool
def call_db2(payload: str, requested_filed):
    """
    Send a message to the DB2  database to fetch any missing fields.

    Args:
        payload (str): The message payload to send.
        requested_filed (str): field that needed to fetch from the Database.

    Returns:
        str: A string or json contain the value of the requested field.
    """
     
    try:
         
        print_colored(f"Connecting to DB2 using ODBC to fetch {requested_filed} ", "36")  # Cyan
        print_colored(f"Result from DB2: {requested_filed} : Canada ", "32")  # Green
        return f"your requestion is completed and the value of the requested feild {requested_filed} is oldAddress.country=Canada"
    except Exception as e:
        print_colored(f"Error: {e}", "31")  # Red
        return f"ailed to fetch {requested_filed} from DB2"    
    
@tool
def call_agent_dataSource( requested_information , payload: str,):
    """
    This to request more information from Data source agent to help in the decision making.

    Args:
        payload (str): The message payload to send.
        requested_filed (str): information that is needed from the data source

    Returns:
        str: A string or json contain the value of the requested field.
    """
    try:
        tools = [call_generic_api]
        model = AzureChatOpenAI(
            deployment_name="gpt-4o-mini",
            model_name="gpt-4o-mini"
        )
        agent = Agent(model, tools, system=PROMPT_DMO)

        # Create a structured message combining requested info and payload
        structured_message = {
            "requested_information": requested_information,
            "context": payload
        }
        
        messages = [HumanMessage(content=str(structured_message))]
        result = agent.graph.invoke({"messages": messages})
        
        print_colored("Welcome to the Data Agent!", "36")  # Cyan
        print_colored(result, "32")  # Green
        
        # Print all messages in the result in ascending order
        for message in result['messages']:
            print_colored(message.content, "32")  # Green
        
        return result['messages'][0].content
    except Exception as e:
        print_colored(f"Error: {e}", "31")  # Red
        return f"Failed to fetch {requested_information} from DMO"

def get_oauth_token():
    """
    Retrieve an OAuth 2.0 token from the APIM.

    Returns:
        str: The OAuth 2.0 token.
    """
    try:
        print ("geting oauth 2.0 token")
        auth_url = os.getenv("APIM_AUTH_URL")
        client_id = os.getenv("APIM_CLIENT_ID")
        client_secret = os.getenv("APIM_CLIENT_SECRET")
        scope = os.getenv("APIM_SCOPE")

        response = requests.post(auth_url, data={
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': scope,
            'grant_type': 'client_credentials'
        })
        response.raise_for_status()
        token = response.json().get('access_token')
        return token
    except requests.RequestException as e:
        print_colored(f"Error obtaining OAuth token: {e}", "31")  # Red
        return None

@tool
def call_generic_api(api_details: dict):
    """
    Make a network call to a generic API based on the provided URL and parameters.

    Args:
        api_details (dict): A dictionary containing the API URL and parameters.
            Example:
            {
                "API": "/endpoint",
                "Parameters": {
                    "param1": "value1",
                    "param2": "value2"
                }
            }

    Returns:
        dict: The JSON response from the API call.
    """
    try:
        print_colored("Validating API details...", "34")  # Blue
        if not isinstance(api_details, dict):
            raise ValueError(f"Expected dict, got {type(api_details)}: {api_details}")
        
        print_colored(f"Raw API details: {api_details}", "36")  # Cyan
        
        base_url = os.getenv("BASE_API_URL")
        endpoint = api_details.get("API")
        if not endpoint:
            raise ValueError("Missing 'API' key in api_details")
            
        url = f"{base_url}{endpoint}"
        params = api_details.get("Parameters", {})
        
        print_colored(f"Constructed URL: {url}", "36")  # Cyan
        print_colored(f"Parameters: {params}", "36")  # Cyan
        
        token = get_oauth_token()
        if not token:
            raise ValueError("Failed to obtain OAuth token")
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        print_colored("Making API request...", "34")  # Blue
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        result = response.json()
        print_colored(f"API Response: {result}", "32")  # Green
        return result
        
    except Exception as e:
        error_msg = f"Error making API call: {str(e)}"
        print_colored(error_msg, "31")  # Red
        return {"error": error_msg}

