import openai
import os

# Configuration from config.py
AI_API_KEY = "sk-slkjdjwchsdaqzzjnxtyadmlytekarmprspppyoztlgwqvqs"
AI_MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"
AI_API_URL = "https://api.siliconflow.cn/v1/"
AI_SYSTEM_PROMPT = "You are a helpful assistant."

try:
    client = openai.OpenAI(
        api_key=AI_API_KEY,
        base_url=AI_API_URL
    )
    
    print(f"Testing connection to {AI_API_URL} with model {AI_MODEL_NAME}...")
    
    response = client.chat.completions.create(
        model=AI_MODEL_NAME,
        messages=[
            {"role": "system", "content": AI_SYSTEM_PROMPT},
            {"role": "user", "content": "Hello"}
        ],
        stream=False
    )
    
    print("Response received:")
    print(response.choices[0].message.content)
    print("API Test Successful")

except Exception as e:
    print(f"API Test Failed: {e}")
