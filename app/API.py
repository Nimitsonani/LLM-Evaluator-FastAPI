import requests
import pandas as pd
from dotenv import load_dotenv
import os

#load dotenv path
load_dotenv(dotenv_path='.env')

#load faq data into a list
df = pd.read_csv('app/FAQ.csv')
FAQ_LIST = [{'Prompt': j.prompt, 'Response': j.response} for i, j in df.iterrows()]

msg=''
def update_msg(convo,name):
    global msg
    if name in ['openai/gpt-oss-20b','gemini-2.5-flash']:
        msg = f"I want you to act like a customer support chatbot of an e-commerce website called ShopFusion. {FAQ_LIST} Here is the FAQ data. If you are asked questions that can't be answered from any information available in FAQ data then just say I’m sorry, but I don’t have that information. If you have any other questions about orders, returns, or products, feel free to ask!. Would you like to talk with our customer support team? If the user says yes, then tell them: Here is the phone number +91 12345 67890. {convo} Here is the list of our conversations continue this conversation. If you see an empty list, then that means you need to start and say: Hi, I am a customer support chatbot, or something similar letting the user know that you are a customer support chatbot, and ask how you can help the user. I don't want you to give responses in dict format, list format, or inside quotes. Just give normal text so I can simply pass it to show the user."
    else:
        system_call = [{
            "role": "system",
            "content": f"you are a customer support chatbot of an ecommerce website called ShopFusion. your task is to Reply to the user queries and help user. here is a FAQ list {FAQ_LIST}, answer to the user if you can find relevant information from this FAQ list otherwise say i am sorry but i can't help you with that. dont give reply in dictionary format or list format or between double or single quote only give plain reply without symbols that can break python code. If the user wants to talk with customer support team Here is the phone number +91 12345 67890. try to keep all replies short unless needed. you will be the one starting first so start."
        }]
        convo_call = []
        for i in range(len(convo)):
            if i % 2 == 0:
                convo_call.append({"role":"assistant",
                                   "content":convo[i]['you']})
            else:
                convo_call.append({"role": "user",
                                   "content": convo[i]['user']})
        msg = system_call+convo_call

#request function
def send_request(url, data, header):
    response = requests.post(url=url, json=data, headers=header)
    return response.json()


#all models
def groq(model_name):
    api_key = os.getenv('GROQ_API_KEY')
    api_url = 'https://api.groq.com/openai/v1/responses'
    payload = {
        "model": model_name,
        "input": msg
    }
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    ans = send_request(api_url, payload, headers)
    try:
        return ans['output'][1]['content'][0]['text']
    except Exception as e:
        print(ans)
        print(e)
        return 'this model is not available right now. try other models.'


def mistral(model_name):
    api_key = os.getenv('MISTRAL_API_KEY')
    api_url = 'https://api.mistral.ai/v1/chat/completions'
    payload = {
        'model': model_name,
        "messages": msg
    }
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    ans = send_request(api_url, payload, headers)
    try:
        return ans['choices'][0]['message']['content']
    except Exception as e:
        print(ans)
        print(e)
        return 'this model is not available right now. try other models.'


def gemini(model_name):
    api_key = os.getenv('GEMINI_API_KEY')
    api_url = f'https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent'
    payload = {
        "contents": [{
            "parts": [{
                "text": msg
            }]
        }]
    }
    headers = {
        'x-goog-api-key': api_key,
        'Content-Type': 'application/json'
    }
    ans = send_request(api_url, payload, headers)
    try:
        return ans['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print(ans)
        print(e)
        return 'this model is not available right now. try other models.'


def open_router(model_name):
    api_key = os.getenv('OPEN_ROUTER_API_KEY')
    api_url = 'https://openrouter.ai/api/v1/chat/completions'
    payload = {
        "model": model_name,
        "messages": msg,
        "reasoning": {
            "enabled": True
        }
    }
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    ans = send_request(api_url, payload, headers)
    try:
        return ans["choices"][0]["message"]["content"]
    except Exception as e:
        print(ans)
        print(e)
        return 'this model is not available right now. try other models.'

def llama(model_name):
    api_key=os.getenv('LLAMA_API_KEY')
    api_url='https://api.groq.com/openai/v1/chat/completions'
    payload = {"model": model_name,
        "messages": msg
               }
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    ans = send_request(api_url, payload, headers)
    try:
        return ans["choices"][0]["message"]["content"]
    except Exception as e:
        print(ans)
        print(e)
        return 'this model is not available right now. try other models.'


#model map to get function refrence
MODEL_MAP = {
    'openai/gpt-oss-20b': groq,
    'gemini-2.5-flash': gemini,
    'mistral-large-latest': mistral,
    'allenai/olmo-3.1-32b-think:free': open_router,
    'xiaomi/mimo-v2-flash:free': open_router,
    'deepseek/deepseek-r1-0528:free': open_router,
    'nex-agi/deepseek-v3.1-nex-n1:free': open_router,
    'nvidia/nemotron-3-nano-30b-a3b:free': open_router,
    'kwaipilot/kat-coder-pro:free': open_router,
    'tngtech/deepseek-r1t2-chimera:free': open_router,
    'llama-3.3-70b-versatile':llama,
}
