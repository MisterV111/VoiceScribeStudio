import os
from dotenv import load_dotenv
from openai import OpenAI

# Load the API key from .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

print(f"Using API key: {api_key[:10]}...{api_key[-5:]}")

# Initialize the OpenAI client
client = OpenAI(api_key=api_key)

# List available models
print("Available models:")
models = client.models.list()
model_ids = [model.id for model in models]
print(model_ids)

# Test if gpt-4o is available
if "gpt-4o" in model_ids:
    print("\ngpt-4o is available for your API key.")
    
    # Try using gpt-4o
    try:
        print("\nTesting with gpt-4o...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello world"}
            ]
        )
        print(f"Response: {response.choices[0].message.content}")
        print("Successfully used gpt-4o!")
    except Exception as e:
        print(f"Error using gpt-4o: {str(e)}")
        
        # Try with a different model as fallback
        try:
            fallback_model = "gpt-3.5-turbo"
            print(f"\nTrying fallback model {fallback_model}...")
            response = client.chat.completions.create(
                model=fallback_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say hello world"}
                ]
            )
            print(f"Response with {fallback_model}: {response.choices[0].message.content}")
            print(f"Successfully used {fallback_model}!")
        except Exception as e2:
            print(f"Error using fallback model: {str(e2)}")
else:
    print("\ngpt-4o is NOT available for your API key.")
    print("Available models include:", model_ids[:5], "...") 