from passlib.context import CryptContext
from datetime import datetime,timedelta,timezone
from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import Cookie
import statistics
from dotenv import load_dotenv
import os

from app.conversation_dict import pop_dict,clean_dict,all_conversation
from app.API import update_msg,MODEL_MAP

load_dotenv(dotenv_path='.env')
SECRET_KEY=os.getenv('SECRET_KEY')
ALGORITHM='HS256'

def hash_password(password):
    pwd_context = CryptContext(schemes=['bcrypt'])
    hash_pass = pwd_context.hash(password)
    return hash_pass

def verify_password(user_input,db_input):
    pwd_context = CryptContext(schemes=['bcrypt'])
    return pwd_context.verify(user_input,db_input)

def generate_jwt(user_id):
    now=datetime.now(timezone.utc)
    payload = {'sub':str(user_id),
               'iat':now,
               'exp':now+timedelta(minutes=60)}
    return jwt.encode(payload,SECRET_KEY,algorithm=ALGORITHM)

def verify_jwt(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    except (JWTError,ExpiredSignatureError) as e:
        print(f'jwt {e}')
        clean_dict()
        return False
    else:
        clean_dict()
        pop_dict[str(payload['sub'])]=payload['exp']
        return payload['sub']


def read_cookie(token= Cookie(alias='AuthToken',default=None)):
    try:
        token = token.split(' ')[1]
    except AttributeError:
        token = 'Not-working-token'
    return token

def model_response(query,id_of_user,name):
    if query:
        all_conversation[id_of_user][name].append({'user': query})
    update_msg(all_conversation[id_of_user][name],name)
    models = MODEL_MAP[name]
    return models(name)

def average(data):
    rating_dict={}
    for i in data:
        model_name= i.model
        rating = float(i.rating)
        rating_dict[model_name] = rating_dict.get(model_name,[])
        rating_dict[model_name].append(rating)
    for i in rating_dict:
        rating_dict[i] = round(statistics.mean(rating_dict[i]),2)
    sorted_d = dict(sorted(rating_dict.items(), key=lambda x: x[1], reverse=True))
    return sorted_d
