from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import asyncio

#Load environment variables from an .env file
load_dotenv()


def load_file_content(filename):
    try:
        with open(filename, "rt") as f:
            return {
                "result": f.read()
                    }
    except Exception as e:
        return {
            "error": "Could not load file content",
        }
    
FUNCTIONS = {"load_file_content": load_file_content}
load_file_content_schema = {
    "name": "load_file_content",
    "description": "load the content of a file",
    "parameters": {
        "type": "object",
        "properties": {
            "filename": {
                "type": "string",
                "description": "The name of the file",
            },
        },
        "required": ["filename"],
    },
    "output": {
        "type": "string",
        "description": "The text content of the file",
    },
}

async def handle_tool_call(session, tool_call):
    for fc in tool_call.function_calls:
        f = FUNCTIONS.get(fc.name)
        tool_response = types.LiveClientToolResponse(
            function_responses=[
                types.FunctionResponse(
                    name=fc.name,
                    id=fc.id,
                    response=f(**fc.args),
                )
            ]
        )
    await session.send(tool_response)

async def main():
    client = genai.Client(
        api_key=os.getenv("GOOGLE_API_KEY"),
        http_options={"api_version": "v1alpha"},
    )

    print("Connected to the AI model!")


    model_id = "gemini-2.0-flash-exp"



    # Add search tool
    search_tool = {"google_search": {}}
    code_execution_tool = {"code_execution": {}}

    config = {
        "tools": [{"function_declarations": [load_file_content_schema]}, search_tool, code_execution_tool], 
        "response_modalities": ["TEXT"],
        }
    

    async with client.aio.live.connect(model=model_id, config=config) as session:
        while True:
            message = input("> ")
            print()

            # Exit the loop if the user types "exit"
            if message == "exit":
                print("exiting....")
                break
            # Send the user's message to AI model, marking the end of the turn
            await session.send(input=message, end_of_turn=True)

            # Process responses from the AI
            async for response in session.receive():
                # Process the function call
                if response.tool_call is not None:
                    await handle_tool_call(session, response.tool_call)
                elif response.server_content.model_turn is not None:
                    for part in response.server_content.model_turn.parts:
                        if part.text is not None:
                            print(part.text, end="", flush=True)
            print()

# Run the main function
asyncio.run(main())
