from google import genai
import sounddevice as sd
import numpy as np
from dotenv import load_dotenv
import os
import asyncio

#Load environment variables from an .env file
load_dotenv()

async def main():
    client = genai.Client(
        api_key=os.getenv("GOOGLE_API_KEY"),
        http_options={"api_version": "v1alpha"},
    )

    print("Connected to the AI model!")

    model_id = "gemini-2.0-flash-exp"
    config = {"response_modalities": ["AUDIO"]}

    with sd.OutputStream(
        samplerate=24000,
        channels=1,
        dtype="int16"
    ) as audio_stream:
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
                    if not response.server_content.turn_complete:
                        for part in response.server_content.model_turn.parts:
                            # Get the audio data from the response part and add it to the steam
                            inline_data = part.inline_data
                            audio_data = np.frombuffer(inline_data.data, dtype="int16")
                            audio_stream.write(audio_data)
# Run the main function
asyncio.run(main())