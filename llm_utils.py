import os
import json
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

def generate_bot_response(user_query, student_context):
    """
    Generates a response using Hugging Face Inference API.
    Using Qwen/Qwen2.5-72B-Instruct via the conversational interface.
    """
    client = InferenceClient(
        model="Qwen/Qwen2.5-72B-Instruct",
        token=os.getenv("HUGGINGFACE_TOKEN")
    )
    
    system_prompt = f"""
    You are a helpful 'Parent Bot' for a school portal. 
    Answer questions based ONLY on the following school data:
    {json.dumps(student_context)}
    
    Instructions:
    - If info is missing, say you don't have that record.
    - Be polite and full of details.
    """
    
    try:
        response = client.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"I'm sorry, I'm having trouble connecting to my cloud brain: {str(e)}"

if __name__ == "__main__":
    # Test
    test_context = {"parentProfile": {"name": "Rajeev"}, "children": [{"profile": {"studentName": "Peeyush"}}]}
    print(generate_bot_response("Who is Rajeev?", test_context))
