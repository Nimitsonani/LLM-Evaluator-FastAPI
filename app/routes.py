from fastapi import FastAPI,Request,Form,Response
from fastapi.params import Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from fastapi.responses import RedirectResponse
from datetime import datetime,timezone,timedelta
from fastapi.staticfiles import StaticFiles
import uuid

#file imports
from app.db import User,AsyncSessionLocal,init_db,Rating
from app.functions import hash_password, verify_password, generate_jwt, verify_jwt, read_cookie, model_response, average
from app.conversation_dict import all_conversation

#exceptions imports
from sqlalchemy.exc import IntegrityError

#create tables on startup
@asynccontextmanager
async def lifespan(app:FastAPI):
    await init_db()
    yield


#app instance and templating
app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory='templates')
app.mount('/static',StaticFiles(directory='static'),name='static')

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@app.get('/test')
def test():
    return 'hi'

#routes
@app.get('/')
def home(request : Request,
         token = Depends(read_cookie)):
    is_logged_in = verify_jwt(token)
    return templates.TemplateResponse(name='home.html',request=request,context={'is_logged_in':is_logged_in})

#reigster
@app.get('/register')
def register(request: Request,
             flash: str|None = None):
    return templates.TemplateResponse(name='register.html',request=request,context={'flash':flash})

@app.post('/register')
async def register_post(username: str=Form(...),
                        email: str=Form(...),
                        password: str= Form(...),
                        db:AsyncSession = Depends(get_db)):
    #@ and .com not allowed in username
    if '@' in username and '.com' in username:
        return RedirectResponse(url='/register?flash=invalid+username',status_code=303)

    # hash the password
    new_hash_pass = hash_password(password)
    new_user = User(username=username,email=email,password=new_hash_pass)
    db.add(new_user)

    #integrity check
    try:
        await db.commit()
    except IntegrityError as error:
        if username in str(error.orig).split('DETAIL:')[1]:
            return RedirectResponse(url='/register?flash=username+is+taken',status_code=303)
        else:
            return RedirectResponse(url='/register?flash=email+is+already+registered',status_code=303)
    await db.refresh(new_user)
    return RedirectResponse(url='/login',status_code=303)


#login route
@app.get('/login')
def login(request: Request,
          flash: str|None = None):
    if flash:
        print(flash)
    return templates.TemplateResponse(name='login.html',request=request,context={'flash':flash})

@app.post('/login')
async def post_login(email_or_username: str = Form(...),
                     password: str=Form(...),
                     db: AsyncSession=Depends(get_db)):
    #check if email or username
    if '@' in email_or_username and '.com' in email_or_username:
        find_user = select(User).where(User.email==email_or_username)
    else:
        find_user = select(User).where(User.username==email_or_username)

    #find user object
    user_object = await db.execute(find_user)
    user = user_object.scalar_one_or_none()

    #if user exist then check password
    if user:
        verification = verify_password(password,user.password)
        if verification:
            #set cookie
            token=generate_jwt(user.id)
            response = RedirectResponse(url='/',status_code=303)
            response.set_cookie(key='AuthToken', value=f'Bearer {token}')
            return response
    return RedirectResponse(url='/login?flash=wrong+login+credentials',status_code=303)

@app.get('/logout')
def logout():
    response = RedirectResponse(url='/')
    response.delete_cookie('AuthToken')
    return response

@app.get('/model')
def model(name:str,
          request:Request,
          token = Depends(read_cookie)):

    is_logged_in = verify_jwt(token)

    # create new userid entry in all_convo if not exist
    all_conversation[is_logged_in] = all_conversation.get(is_logged_in, {name: []})
    # create new model entry in userid if not exist
    all_conversation[is_logged_in][name] = all_conversation[is_logged_in].get(name,[])
    if is_logged_in:
        is_logged_in = str(is_logged_in)
        if len(all_conversation[is_logged_in][name])==0:
            bot_response = model_response(None, is_logged_in, name)
            all_conversation[is_logged_in][name].append({'you':bot_response})
        return templates.TemplateResponse(name='chat_page.html',request=request,context={'name':name,'conversation':all_conversation[is_logged_in][name],'is_logged_in':is_logged_in})
    return RedirectResponse(url='/login?flash=login+first')

@app.post('/model')
async def post_model(name: str,
               query:str =Form(...),
               token = Depends(read_cookie)):
    is_logged_in = verify_jwt(token)
    if is_logged_in:
        is_logged_in = str(is_logged_in)
        bot_response = model_response(query,is_logged_in,name)
        all_conversation[is_logged_in][name].append({'you':bot_response})
        return RedirectResponse(url=f'/model?name={name}',status_code=303)

    return RedirectResponse(url='/login?flash=login+first',status_code=303)

@app.post('/rating')
async def give_rating(name: str,
                      token = Depends(read_cookie),
                      rating = Form(...),
                      db: AsyncSession = Depends(get_db)):
    is_logged_in = verify_jwt(token)
    if is_logged_in:
        if 0<float(rating)<=10:
            new_rating = Rating(rating=float(rating), model=name, user_id=uuid.UUID(is_logged_in))
            db.add(new_rating)
            await db.commit()
            await db.refresh(new_rating)
            return RedirectResponse(url='/',status_code=303)
        return "rating must be btwn 0-10"
    return RedirectResponse(url='/login',status_code=303)

@app.get('/last_24_hours_top')
async def last_24_hours(request: Request,
                        db: AsyncSession = Depends(get_db)):
    last_24_hrs = datetime.now(timezone.utc) - timedelta(hours=24)
    select_obj = select(Rating).where(Rating.created_at >= last_24_hrs)
    check_db = await db.execute(select_obj)
    top_24_hrs = check_db.scalars()
    ans = average(top_24_hrs)
    return templates.TemplateResponse(name='top.html',request=request,context={'ans':ans})

@app.get('/weekly_top')
async def weekly_top(request: Request,
                     db: AsyncSession = Depends(get_db)):
    last_7_days = datetime.now(timezone.utc) - timedelta(days=7)
    select_obj = select(Rating).where(Rating.created_at >= last_7_days)
    check_db = await db.execute(select_obj)
    top_7_days = check_db.scalars()
    ans = average(top_7_days)
    return templates.TemplateResponse(name='top.html',request=request,context={'ans':ans})

@app.get('/account')
async def account(request:Request,
                  token = Depends(read_cookie),
                  db: AsyncSession = Depends(get_db)):
    is_logged_in = verify_jwt(token)
    if is_logged_in:
        is_logged_in = uuid.UUID(is_logged_in)
        user_obj1 = select(User).where(User.id==is_logged_in)
        user_obj2 = await db.execute(user_obj1)
        user = user_obj2.scalar_one_or_none()
        return templates.TemplateResponse(name='account.html',request=request,context={'username':user.username})
    return RedirectResponse('/login?flash=login+first')

@app.get('/my_ratings')
async def my_ratings(request:Request,
                  token = Depends(read_cookie),
                  db: AsyncSession = Depends(get_db)):
    is_logged_in = verify_jwt(token)
    if is_logged_in:
        is_logged_in = uuid.UUID(is_logged_in)
        user_obj1 = select(User).where(User.id == is_logged_in)
        user_obj2 = await db.execute(user_obj1)
        user = user_obj2.scalar_one_or_none()
        return templates.TemplateResponse(name='my_rating.html', request=request, context={'username': user.username,'ratings':user.all_rating})
    return RedirectResponse(url='/login?flash=login+first')

@app.get('/change_password')
async def change_password(request:Request,
                          flash: str|None = None,
                          token = Depends(read_cookie)):
    is_logged_in = verify_jwt(token)
    if is_logged_in:
        return templates.TemplateResponse(name='change_password.html', request=request, context={'flash':flash})
    return RedirectResponse(url='/login?flash=login+first')

@app.post('/change_password')
async def post_change_password(new_password: str = Form(...),
                                confirm_password: str = Form(...),
                                token = Depends(read_cookie),
                                db: AsyncSession = Depends(get_db)):
    is_logged_in = verify_jwt(token)
    if is_logged_in:
        is_logged_in = uuid.UUID(is_logged_in)
        user_obj1 = select(User).where(User.id == is_logged_in)
        user_obj2 = await db.execute(user_obj1)
        user = user_obj2.scalar_one_or_none()

        #check if both password match
        if new_password == confirm_password:

            #update password
            user.password = hash_password(new_password)
            await db.commit()
            return RedirectResponse(url='/account', status_code=303)
        return RedirectResponse(url='/change_password?flash=new+password+do+not+match', status_code=303)

    return RedirectResponse(url='/login?flash=login+first',status_code=303)


@app.get('/change_username')
async def change_username(request: Request,
                          flash: str | None = None,
                          token=Depends(read_cookie)):
    is_logged_in = verify_jwt(token)
    if is_logged_in:
        return templates.TemplateResponse(name='change_username.html', request=request,
                                          context={'flash': flash})
    return RedirectResponse(url='/login?flash=login+first')


@app.post('/change_username')
async def post_change_username(new_username: str = Form(...),
                               token=Depends(read_cookie),
                               db: AsyncSession = Depends(get_db)):
    is_logged_in = verify_jwt(token)
    if is_logged_in:
        is_logged_in = uuid.UUID(is_logged_in)
        user_obj1 = select(User).where(User.id == is_logged_in)
        user_obj2 = await db.execute(user_obj1)
        user = user_obj2.scalar_one_or_none()

        # check for integrity
        if '@' in new_username and '.com' in new_username:
            return RedirectResponse(url='/change_username?flash=invalid+username', status_code=303)
        user.username=new_username
        try:
            await db.commit()
        except IntegrityError:
            return RedirectResponse(url='/change_username?flash=username+is+taken', status_code=303)
        return RedirectResponse(url='/account', status_code=303)

    return RedirectResponse(url='/login?flash=login+first',status_code=303)


# @app.get('/random_rating')
# async def random_rating(db:AsyncSession = Depends(get_db)):
#     import random
#     for i in range(100):
#         rating = round(random.random() * 10, 2)
#
#         name = random.choice(
#             ['openai/gpt-oss-20b', 'gemini-2.5-flash', 'mistral-large-latest', 'allenai/olmo-3.1-32b-think:free',
#              'xiaomi/mimo-v2-flash:free', 'deepseek/deepseek-r1-0528:free', 'nex-agi/deepseek-v3.1-nex-n1:free',
#              'nvidia/nemotron-3-nano-30b-a3b:free', 'kwaipilot/kat-coder-pro:free',
#              'tngtech/deepseek-r1t2-chimera:free'])
#         day=random.choice([27,30])
#         new_rating = Rating(rating=float(rating), model=name, user_id=uuid.UUID('7e27ab3c-3f99-4e9f-8308-a3975c2761f6'),
#                             created_at=datetime(2025,12,day,11,1,tzinfo=timezone.utc))
#         db.add(new_rating)
#         await db.commit()
#     return 'done'
