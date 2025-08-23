from pydantic import BaseModel
import rich
from connections import config
import asyncio
from agents import input_guardrail,output_guardrail,InputGuardrailTripwireTriggered,OutputGuardrailTripwireTriggered,GuardrailFunctionOutput,Agent,Runner
class Child_Agent_Output(BaseModel):
    response:str
    isACCelsiusExceed:bool
father_agent = Agent(
     name='Father Agent',
     instructions='You are a father Agent, your job is to stop your child from running AC below 26 degree Celsius.',
     output_type=Child_Agent_Output   
)
@input_guardrail
async def ACTempGuadrail(ctx,agent,input):
    result  = await Runner.run(
        father_agent,
        input,
        run_config=config    
    )
    
    print('Father Agent',result.final_output)
    return GuardrailFunctionOutput(
        output_info=result.final_output.response,
        tripwire_triggered=result.final_output.isACCelsiusExceed
    )
  
child_agent = Agent(
  name='Child Agent',
  instructions='You are a Child Agent',
  input_guardrails=[ACTempGuadrail]
)
async def main():
    try:
        result = await Runner.run(
            child_agent,
            'My AC temp is 7 Celsius',
            run_config=config
        )
        print('Child is Doing OK!!')
    except InputGuardrailTripwireTriggered as e:
        print('Child is not doing Good',e)     

if __name__ == "__main__":
    asyncio.run(main())        