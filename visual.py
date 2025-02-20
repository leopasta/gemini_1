from google import genai
from dotenv import load_dotenv
import os
from PIL import Image


load_dotenv()


def load_and_resize_image(image_path):
    with Image.open(image_path) as img:
        aspect_ratio = img.height / img.width
        new_height = int(img.width * aspect_ratio)
        return img.resize((img.width, new_height), Image.Resampling.LANCZOS)
    
image = load_and_resize_image("sample.jpg")

client = genai.Client(
    api_key = os.getenv("GOOGLE_API_KEY"),
    http_options={"api_version": "v1alpha"},
)

response = client.models.generate_content(
    model="gemini-2.0-flash-exp",
    contents=["Describe the image", image],
)

print(response.text)