from pydantic import BaseModel
import rich
from connections import config
import asyncio
from agents import input_guardrail,output_guardrail,InputGuardrailTripwireTriggered,OutputGuardrailTripwireTriggered,GuardrailFunctionOutput,Agent,Runner

class Student_Output(BaseModel):
    response:str
    student_request:bool

giaic_admin_agent = Agent(
    name='GIAIC Admin Agent',
    instructions="""

    you are an GIAIC admin agent, you are responsible for managing the GIAIC Management.There three classes and all are on weekdays, the timings are 8am-10am 11am-1pm and 2pm-4pm course is only one and that is Learn Agentic AI,If someone ask you about anything else than GIAIC do not answer them
""",
   output_type=Student_Output

)
@input_guardrail
async def security_guadrail(ctx,agent,input):
    result = await Runner.run(
        giaic_admin_agent,
        input,
        run_config=config,    
                )
    return GuardrailFunctionOutput(
        output_info=result.final_output.response,
        tripwire_triggered= True#result.final_output.student_request
        

    )
student_agent = Agent(
    name = 'GIAIC Student Agent',
    instructions="""
    you are a GIAIC student agent
    """,
    input_guardrails=[security_guadrail]
)

async def main():
    try:
        result = await Runner.run(
            student_agent,
            "I want to change my class timings 😭😭",
            run_config=config,
        ) 
        rich.print(result.final_output)
    except InputGuardrailTripwireTriggered:
        rich.print('Request did not sent! Contact Admministration')    

if __name__ == "__main__":
    asyncio.run(main())        