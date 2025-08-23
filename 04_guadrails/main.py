from pydantic import BaseModel
import rich
from connections import config
import asyncio
from agents import input_guardrail,output_guardrail,InputGuardrailTripwireTriggered,OutputGuardrailTripwireTriggered,GuardrailFunctionOutput,Agent,Runner
class Student_output(BaseModel):
    response:str
    isUniformColorChanged:bool
class Gate_keeper_output(BaseModel):
    response:str
    isRude:bool    

@input_guardrail
async def uniform_checker(ctx,agent,input):
    result = await Runner.run(
        gate_keeper_agent,
        input,
        run_config=config,
    )
    rich.print(result.final_output)
    return GuardrailFunctionOutput(
        output_info=result.final_output.response,
        tripwire_triggered=result.final_output.isUniformColorChanged
    )

@output_guardrail
async def gate_keeper_response(ctx,agent,output):
    result = await Runner.run(
        filter_guard_response,
        output.response,run_config=config

    ) 
    rich.print('Output Guardrail',result.final_output)
    return GuardrailFunctionOutput(
        output_info=result.final_output.response,
        tripwire_triggered= result.final_output.isRude
    )
filter_guard_response = Agent(
    name="Filter Guard Agent",
    instructions="""
      1- your job is to check the response of gate keeper agent
      2- you will check politeness of the gate keeper agent towards the student
      3- if gate keeper agent marks contains offensive, disrepectful or insulting language the tripwire triggered = True
      4- Do not mark denials as policy violations.
""",
    output_type=Gate_keeper_output

)

gate_keeper_agent = Agent(
    name='Gate Keeper Agent',
    instructions="""
     You are a politeness checker for the Gate Keeper Agent's messages to students.

Mark `isRude=True` ONLY if the message:
- Contains direct insults, name-calling, mocking, or sarcasm.
- Uses profanity or offensive slurs.
- Shows hostile or aggressive tone towards the student.

Do NOT mark as rude if the message:
- States school policies.
- Explains the reason for denial, even if it mentions 'abusive language' or 'rule violation'.
- Uses neutral, factual, or professional wording.

Output `isRude=False` for any polite or factual statements, even if they deny entry.  
 """,
   output_type=Student_output,
    output_guardrails=[gate_keeper_response]
)
student_agent = Agent(
   name='Student Agent',
   instructions="""
       You are a student agent your job is to go to school and wear a proper uniform of that school
     """,
    input_guardrails=[uniform_checker] 
  
)

async def main():
    try:
        result = await Runner.run(
            student_agent,
            "my uniform is white shirt and blue pant you idiot",
            run_config=config

        ) 
        print('you are allow to enter the school.')    

    except InputGuardrailTripwireTriggered as e:
        print('You can not enter in the school',e)   
    except OutputGuardrailTripwireTriggered as e:
        print("Gate Keeper response was blocked by output guardrail")    
        # rich.print(result.final_output) 
if __name__ == "__main__":
    asyncio.run(main())  