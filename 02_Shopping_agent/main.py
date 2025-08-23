from agents import Agent,function_tool,Runner
from connection import config
import chainlit as cl
import requests

@function_tool
def shopping_tool():
    api_data = 'https://template6-six.vercel.app/api/products'
    try:
        response = requests.get(api_data)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.HTTPError:
        return f"Sorry i couldn't fetch the data from api" 
    except requests.exceptions.RequestException as e:
        return f"the error: ${e}"   

agent = Agent(
    name= "shopping agent",
    instructions='You are a shopping agent your job is to use tool and answer the queries of users',
    tools=[shopping_tool])
@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set('history',[])
    await cl.Message(content = 'Welcome to the Shopping Agent! Ask me about the Products prices and details.').send()
@cl.on_message
async def handle_message(msg):
    history = cl.user_session.get('history')
    history.append({'role':'user', 'content':msg.content})

    result = Runner.run_sync(
        agent,
        input = history,
        run_config = config
    )
    history.append({"role": "assistant", "content": result.final_output})
    cl.user_session.set("history", history)

    
    await cl.Message(content=result.final_output).send()
