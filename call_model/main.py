import requests

MODEL_API_URL = "http://localhost:12434/engines/v1/chat/completions"
MODEL_NAME = "ai/gemma3:latest" 

def ask_gemma():

    system_prompt = "You are a joker who makes people laugh with the funniest jokes"
    user_prompt = "Tell me the funniest joke you know"

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.1, 
        "max_tokens": 150
    }

    try:
        response = requests.post(MODEL_API_URL, json=payload, headers={"Content-Type": "application/json"})
        
        if response.status_code != 200:
            return {"status": "ERROR", "reason": f"HTTP {response.status_code}: {response.text}"}
            
        result_text = response.json()["choices"][0]["message"]["content"]
        
        return result_text

    except Exception as e:
        return {"status": "ERROR", "reason": str(e)}
    
print(ask_gemma())
