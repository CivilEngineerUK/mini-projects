import openai
import json
import yfinance as yf
import time

class AssistantManager:
    def __init__(self):
        self.client = openai.OpenAI()

    def run_assistant_and_process(self, content, assistant_name, instructions,
                                  tools_list, function_mapping, model_name="gpt-4-1106-preview"):
        self.function_mapping = function_mapping
        self.assistant = self.client.beta.assistants.create(
            name=assistant_name,
            instructions=instructions,
            tools=tools_list,
            model=model_name,
        )

        # Create thread and message as part of the initialization
        self.thread = self.client.beta.threads.create()
        self.message = self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=content
        )

        self.run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
            instructions=instructions
        )

        while True:
            time.sleep(1)
            run_status = self.client.beta.threads.runs.retrieve(thread_id=self.thread.id, run_id=self.run.id)

            if run_status.status == 'completed':
                self.process_completed_run(self.thread)
                break
            elif run_status.status == 'requires_action':
                self.process_required_action(self.thread, run_status, self.run)
            else:
                print("Waiting for the Assistant to process...")

    def process_completed_run(self, thread):
        messages = self.client.beta.threads.messages.list(thread_id=thread.id)
        for msg in messages.data:
            role = msg.role
            content = msg.content[0].text.value
            print(f"{role.capitalize()}: {content}")

    def process_required_action(self, thread, run_status, run):
        print("Function Calling")
        required_actions = run_status.required_action.submit_tool_outputs.model_dump()
        tool_outputs = []

        for action in required_actions["tool_calls"]:
            func_name = action['function']['name']
            arguments = json.loads(action['function']['arguments'])

            if func_name in self.function_mapping:
                try:
                    output = self.function_mapping[func_name](**arguments)
                    tool_outputs.append({
                        "tool_call_id": action['id'],
                        "output": output
                    })
                except Exception as e:
                    print(f"Error executing {func_name}: {e}")
            else:
                print(f"Unknown function: {func_name}")

        self.client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=tool_outputs
        )

# Usage example:

# create simple schema for a mathematical expression
from pydantic import BaseModel, Field
from instructor import OpenAISchema
from typing import List, Optional

class Variable(BaseModel):
    variable: str = Field(..., description="Variable name")
    value: Optional[str] = Field(..., description="Variable value")
    unit: str = Field(..., description="Variable unit")

class SimpleCalculation(OpenAISchema):
    name: str = "simply_supported_beam_deflection"
    description: str = "Calculate the deflection of a simply supported beam"
    expression: str = Field(..., description="Expression to calculate")
    lead_variable: Variable = Field(..., description="Lead variable. You must calculate the value using the 'expression' and 'values'")
    variables: List[Variable] = Field(..., description="List of variables")

class FixedCalculation(OpenAISchema):
    name: str = "fixed_beam_deflection"
    description: str = "Calculate the deflection of a fixed support beam"
    expression: str = Field(..., description="Expression to calculate")
    lead_variable: Variable = Field(..., description="Lead variable. You must calculate the value using the 'expression' and 'values'")
    variables: List[Variable] = Field(..., description="List of variables")

tools_list = [
    SimpleCalculation.openai_schema,
    FixedCalculation.openai_schema
]

def simply_supported_beam_deflection(L, P, E, I):
    return (P * L ** 3) / (48 * E * I)

def fixed_beam_deflection(L, P, E, I):
    return (P * L ** 3) / (192 * E * I)


function_mapping = {
    "simply_supported_beam_deflection": simply_supported_beam_deflection,
    "fixed_beam_deflection": fixed_beam_deflection
}

# Initialize AssistantManager with content
assistant_manager = AssistantManager()

model = "gpt-4-1106-preview"

# Run assistant and process the result
assistant_manager.run_assistant_and_process(
    #"Calculate the deflection of a simply supported beam with a length of 5m, a central point load of P = 10kN and constant EI of 1kN*m^2",
    "Calculate the deflection of a fixed support beam with a length of 5m, a central point load of P = 10kN, E = 1e3Kn/m^2 and I = 1m^4"
    " Use the functions provided - do not rely on your internal memory",
    assistant_name="structural_engineering_assistant",
    instructions="Use the most relevant provided function and include its name in your response",
    tools_list=tools_list,
    function_mapping=function_mapping,
    model_name=model,
)
