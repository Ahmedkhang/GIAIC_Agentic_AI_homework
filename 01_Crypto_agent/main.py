from agents import Agent, function_tool, Runner, RunConfig ,OpenAIChatCompletionsModel,AsyncOpenAI
import requests
import chainlit as cl
from dotenv import load_dotenv

import os

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
@function_tool
# This tool fetches the current price of a cryptocurrency in USDT from Binance API.
def crypto_agent(symbol:str) -> str:
    symbol = symbol.upper() + 'USDT'
    crypto_api = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"

    try:
        response = requests.get(crypto_api)
        response.raise_for_status()
        data = response.json()
        price = data.get('price')
        return f"The Current Price of ${symbol} is ${price}"
    except requests.exceptions.HTTPError:
        return f"Sorry, I couldn't fetch the price for ${symbol}. Please check the currency symbol and try again."    
    except requests.exceptions.RequestException as e:
        return f"An error occurred while fetching the price: {str(e)}"
    
client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/"
)

model = OpenAIChatCompletionsModel(
    model='gemini-2.0-flash',
    openai_client=client
)
config = RunConfig(
    model=model,
    model_provider=client,
    tracing_disabled=True
)

agent = Agent(
    name='Crypto Agent',
    instructions='You are a Crypto Agent, You will provide the latest prices of cryptocurrencies in USDT. If the user asks for a currency that is not available, you will inform them.and make sure to use the tool crypto_agent to get the price.',
    tools=[crypto_agent],
)
@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set('history',[])
    await cl.Message(content = 'Welcome to the Crypto Agent! Ask me about the latest cryptocurrency prices in USDT.').send()
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
