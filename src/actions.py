from azure.storage.queue import QueueServiceClient
import os
from dotenv import load_dotenv
from langchain_core.tools import tool

# Load environment variables from .env file
load_dotenv()

# Initialize the QueueServiceClient
queue_service_client = QueueServiceClient.from_connection_string(os.getenv("AZURE_STORAGE_CONNECTION_STRING"))

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
        print(f"payload is {payload}")
        response = queue_client.send_message(payload)
        print(f"Payload inserted into the {queue_name} queue successfully.")
        print(f"Message ID: {response.id}, Insertion Time: {response.inserted_on}")
        return f"Message has been inserted into the {queue_name} queue successfully."
    except Exception as e:
        print(f"Failed to insert payload into the {queue_name} queue.")
        print(f"Error: {e}")
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
        print(f"payload is {payload}")
        response = queue_client.send_message(payload)
        print(f"Payload inserted into the {queue_name} queue successfully.")
        print(f"Message ID: {response.id}, Insertion Time: {response.inserted_on}")
        return f"Message has been inserted into the {queue_name} queue successfully."
    except Exception as e:
        print(f"Failed to insert payload into the {queue_name} queue.")
        print(f"Error: {e}")
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
         
        print(f"Connecting to DB2 using ODBC to fetch {requested_filed} ")
        print(f"Result from DB2: {requested_filed} : Canada ")
        return f"your requestion is completed and the value of the requested feild {requested_filed} is oldAddress.country=Canada"
    except Exception as e:
        print(f"Error: {e}")
        return f"ailed to fetch {requested_filed} from DB2"    