import random
from boto3.dynamodb.conditions import Key
import time
import datetime
from swarm import Agent
from swarm.repl import run_demo_loop
import json
from swarm import Swarm
import dotenv
dotenv.load_dotenv()
import boto3
from botocore.exceptions import ClientError
from swarm import Agent



def generate_ppt(ppt_content):
    """Generate PowerPoint content based on a single formatted string."""
    print(f"[mock] Generating PPT with content: {ppt_content}")
    return ppt_content

def generate_csv(data_topic, num_rows):
    """Generate CSV content based on user input."""
    print(f"[mock] Generating CSV with topic '{data_topic}' and {num_rows} rows...")
    csv_content = "\n".join([f"Row {i+1}, Data {random.randint(1, 100)}" for i in range(num_rows)])
    return csv_content

triage_agent = Agent(
    name="Triage Agent",
    model="gpt-4o-mini",
    instructions="Determine which agent is best suited to handle the user's request, and transfer the conversation to that agent.",
)

ppt_maker_agent = Agent(
    name="PPT Maker Agent",
    model="gpt-4o-mini",
    instructions=(
        "Ask the user for number of slides and Topics. "
        "Then generate structured PowerPoint content in the format: "
        "<TITLES>Titles1<SEP>Title2<SEP>Title3<CONTENT>Content1<SEP>Content2<SEP>Content3. "
        "Ensure the titles align with the content and pass a single formatted string to the function."
    ),
    functions=[generate_ppt],
)

csv_maker_agent = Agent(
    name="CSV Maker Agent",
    model="gpt-4o-mini",
    instructions="Ask the user for a data topic and number of rows, then generate CSV data.",
    functions=[generate_csv],
)

def transfer_back_to_triage():
    """Call this function if a user is asking about a topic that is not handled by the current agent."""
    return triage_agent

def transfer_to_ppt_maker():
    return ppt_maker_agent

def transfer_to_csv_maker():
    return csv_maker_agent

triage_agent.functions = [transfer_to_ppt_maker, transfer_to_csv_maker]
ppt_maker_agent.functions.append(transfer_back_to_triage)
csv_maker_agent.functions.append(transfer_back_to_triage)

def get_current_agent(session_id):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('idocgen_sessions')
    try:
        response = table.get_item(Key={'session_id': session_id})
        return response['Item']['current_agent']
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"No session found for session_id: {session_id}")
            return 'triage'
        else:
            raise

def get_messages(session_id):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('idocgen_messages')
    response = table.query(
        KeyConditionExpression=Key('session_id').eq(session_id)
    )
    messages = response.get('Items', [])
    if not messages:
        print(f"No messages found for session_id: {session_id}")
        messages = []
    return messages

def save_messages_to_dynamodb(session_id, messages):
    """Save messages to DynamoDB table."""

    dynamodb = boto3.resource('dynamodb' , region_name='ap-south-1')
    # Replace 'MessagesTable' with your DynamoDB table name
    table = dynamodb.Table('idocgen_messages')
    # Save messages to DynamoDB

    print("THE TABLE OBJECT IS : " , table)
    print("THE TABLE NAME IS : " , table.table_name)

    current_agent = get_current_agent(session_id)
    agent = agents[current_agent]

    for message in messages:
        try:
            response = table.put_item(
                Item={
                    'session_id': session_id,
                    'message': message['content'] , 
                    'time_stamp' :str(time.time()) ,
                    'agent':message['role'] 
                }   
            )
            print("Messages saved to DynamoDB" , response)
        except ClientError as e:
            print(f"Failed to save messages: {e.response['Error']['Message']}")

def run_demo_loop(
    starting_agent, context_variables=None, stream=False, debug=False
) -> None:
    client = Swarm()
    print("Starting Swarm CLI 🐝")

    '''
    take session_id instead of starting_agent 
    current_agent = get_current_agent(session_id)
    agent = agents[current_agent] ** important as agent object is required 
    messages = get_messages(session_id)
    '''



    messages = [] # get by session_id 
    agent = starting_agent # get by session_id ( but it will be a string value ) 
    current_agent = ''



    
    user_input = input("\033[90mUser\033[0m: ")
    messages.append({"role": "user", "content": user_input})

    print("MESSAGES ARE : ")
    print(messages)

    response = client.run(
        agent=agent,
        messages=messages,
        context_variables=context_variables or {},
        stream=stream,
        debug=debug,
    )
    messages.extend(response.messages)
    # Initialize a session using Amazon DynamoDB
   
    save_messages_to_dynamodb(session_id='example_session_id', messages=response.messages)

    agent = response.agent



agents = {
    "triage": triage_agent,
    "ppt_maker": ppt_maker_agent,
    "csv_maker": csv_maker_agent,
    "transfer_back_to_triage": transfer_back_to_triage,
    "transfer_to_ppt_maker": transfer_to_ppt_maker,
    "transfer_to_csv_maker": transfer_to_csv_maker,
}

def handler(event, context):
    data = event
    session_id = data['session_id']
    message = {
        "role": "user",
        "content": data['message']
    }
    messages = get_messages(session_id)
    messages.append({"role": "user", "content": message})

    save_messages_to_dynamodb(session_id=session_id, messages=[message])
    run_demo_loop(triage_agent, debug=False)


session_id = input("Enter session id : ")
message = input("Enter your message : ")

event = {
    'session_id': session_id,
    'message': message
}

handler(event , '')
