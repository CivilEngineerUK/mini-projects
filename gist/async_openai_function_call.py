"""
Title: Asynchronous OpenAI API Wrapper with Error Handling

Description: A Python script to interact with the OpenAI API asynchronously, with built-in error handling and retry logic.
This script is designed to handle multiple prompts with the ability to define custom functions for more complex queries.
Created from guidance at: https://platform.openai.com/docs/guides/gpt/function-calling

Updated: rev 1 - 16/11/2023 for new end point and gpt-4-1106-preview [openai==1.2.4]
               - includes structural engineering beam formula schema and use of Pydantic and instructor

Author: @CivilEngineerUK
"""

import asyncio
import json
import openai
from pydantic import BaseModel, Field
from instructor import OpenAISchema
from typing import List, Optional


class OpenAI_ASync:
    def __init__(self):
        self.client = openai.AsyncOpenAI()

    async def openai_api_call(self, func, **kwargs):
        max_retries = 5
        retry_count = 0
        base_wait_time = 1

        while retry_count <= max_retries:
            try:
                return await func(**kwargs)
            except (openai.error.APIError,
                    openai.error.APIConnectionError,
                    openai.error.RateLimitError,
                    openai.error.Timeout,
                    openai.error.ServiceUnavailableError) as e:
                error_messages = {
                    openai.error.APIError: "Issue on OpenAI's side.",
                    openai.error.APIConnectionError: "Failed to connect to OpenAI API.",
                    openai.error.RateLimitError: "Rate limit exceeded.",
                    openai.error.Timeout: "Request timed out.",
                    openai.error.ServiceUnavailableError: "Service unavailable."
                }
                error_message = error_messages.get(type(e), "Unknown error.")
                print(f"{error_message} Retrying... {2 ** retry_count}s")
                retry_count += 1
                await asyncio.sleep(base_wait_time * (2 ** retry_count))
            except (openai.error.AuthenticationError, openai.error.InvalidRequestError) as e:
                error_messages = {
                    openai.error.AuthenticationError: "Authentication error. Check API key or token.",
                    openai.error.InvalidRequestError: "Invalid request. Check parameters and retry."
                }
                print(error_messages.get(type(e), "Unknown error."))
                return None
            except Exception as e:
                print(f"Unexpected error: {e}. Exiting...")
                return None

        print("Max retries reached. Exiting...")
        return None

    async def handle_multiple_prompts(self, prompts, model, functions=None,
                                      function_call="auto", temperature=0.0):
        tasks = [self.create_chat_completion(prompt, model, functions, function_call,
                                             temperature=temperature) for prompt in prompts]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        return responses

    async def create_chat_completion(self, prompt, model="gpt-3.5-turbo-0613", functions=None, function_call="auto",
                                     temperature=0.0):
        async def api_call():
            return await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                functions=functions,
                function_call=function_call,
                temperature=temperature
            )

        response = await self.openai_api_call(api_call)

        return response


# Usage example:

# create simple schema for a mathematical expression
class Variable(BaseModel):
    variable: str = Field(..., description="Variable name")
    value: Optional[str] = Field(..., description="Variable value")
    unit: str = Field(..., description="Variable unit")

class SimpleCalculation(OpenAISchema):
    expression: str = Field(..., description="Expression to calculate")
    lead_variable: Variable = Field(..., description="Lead variable. You must calculate the value using the 'expression' and 'values'")
    variables: List[Variable] = Field(..., description="List of variables")

functions = [SimpleCalculation.openai_schema]

# Create an instance of the OpenAI_ASync class
openai_async = OpenAI_ASync()

# Define the prompts
beam = "5m simply supported beam with a central point load of P = 10kN and constant EI"
prompts = [
    f"Bending moment formula: {beam}",
    f"Deflection formula: {beam}",
    f"Shear force formula: {beam}"
]

# Define model
model = "gpt-4-1106-preview"

async def main() -> None:

    # Get the responses
    responses = await openai_async.handle_multiple_prompts(
        prompts, model, functions, function_call="auto", temperature=0.0)

    for response in responses:
        # Extracting the arguments into dict
        arguments_dict = json.loads(response.choices[0].message.function_call.arguments)

        print(arguments_dict)

asyncio.run(main())