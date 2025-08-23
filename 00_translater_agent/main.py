from agents import Agent,AsyncOpenAI,Runner,RunConfig,OpenAIChatCompletionsModel
from dotenv import load_dotenv
import os

load_dotenv()
gemini_api_key  = os.getenv('GEMINI_API_KEY')
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
if not gemini_api_key:
    raise ValueError('API KEY not found!!') 

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)
agent_Translater = Agent(
    name = 'Translater Agent',
    instructions= 'You are helpful translater who can translate any paragraph,essay to any language'
)
print('---------- Welcome to Agent Translater ----------')
# while True:
user_input  =input('ENter a sentence to translate ( or press q to quit ): ')
    # if user_input.lower() == 'q':
        # break/
    
response  = Runner.run_sync(
    agent_Translater,
    # input = 'Translate me berozgaar hu into english',
    
    input = user_input,
    run_config = config
)

print(response.final_output)