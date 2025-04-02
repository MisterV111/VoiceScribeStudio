from deepseek import DeepSeekAPI
from ..config import DEEPSEEK_API_KEY, DEEPSEEK_MODEL

# Initialize DeepSeek client
if DEEPSEEK_API_KEY:
    client = DeepSeekAPI(api_key=DEEPSEEK_API_KEY)
else:
    client = None
    print("Warning: DEEPSEEK_API_KEY not found. DeepSeek functionality will be disabled.")

def generate_script_with_deepseek(system_message, user_message, model=DEEPSEEK_MODEL):
    """
    Generate a script using the DeepSeek API.
    
    Args:
        system_message (str): The system prompt guiding the model.
        user_message (str): The user's prompt and context.
        model (str): The DeepSeek model to use (e.g., deepseek-chat).
        
    Returns:
        str: The generated script, or None if an error occurs.
    """
    if not client:
        print("DeepSeek client not initialized. Skipping generation.")
        return None
        
    try:
        print(f"Attempting script generation with DeepSeek model: {model}")
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7, # Adjust as needed
            max_tokens=3000  # Adjust based on DeepSeek model limits and desired output length
        )
        
        if completion.choices and completion.choices[0].message:
            generated_content = completion.choices[0].message.content
            print(f"DeepSeek generated {len(generated_content.split())} words.")
            return generated_content
        else:
            print("DeepSeek response did not contain expected content.")
            return None
            
    except Exception as e:
        print(f"Error generating script with DeepSeek model {model}: {str(e)}")
        import traceback
        traceback.print_exc() # Print full traceback for debugging
        return None 