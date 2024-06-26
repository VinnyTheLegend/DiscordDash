import os
import json
import secret

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import RedirectResponse, JSONResponse

from starlette.datastructures import URL

from authlib.integrations.httpx_client import AsyncOAuth2Client

from database import crud, models, schemas 
from database.database import SessionLocal, engine

from utils.limiter import limiter
from utils import utils

OAUTH2_CLIENT_ID = secret.OAUTH2_CLIENT_ID
OAUTH2_CLIENT_SECRET = secret.OAUTH2_CLIENT_SECRET
OAUTH2_REDIRECT_URI = secret.OAUTH2_REDIRECT_URI

GUILD_ID = secret.GUILD_ID

FRONT_URI = secret.FRONT_URI

API_BASE_URL = 'https://discord.com/api'
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'
SCOPE = 'identify guilds.members.read'

if 'http://' in OAUTH2_REDIRECT_URI:
    os.environ['AUTHLIB_INSECURE_TRANSPORT'] = 'true'

models.Base.metadata.create_all(bind=engine)

router = APIRouter()

@router.get('/discord/authenticate')
async def index(request: Request):
    client = AsyncOAuth2Client(
        client_id=OAUTH2_CLIENT_ID,
        client_secret=OAUTH2_CLIENT_SECRET,
        redirect_uri=OAUTH2_REDIRECT_URI,
        scope=SCOPE)
    
    authorization_url, state = client.create_authorization_url(AUTHORIZATION_BASE_URL)
    print('new state: ', state)
    request.session['oauth2_state'] = state

    return RedirectResponse(url=authorization_url)


@router.get('/discord/callback')
@limiter.limit("1/minute")
async def callback(request: Request, code: str = None, state: str = None):
    if code is None or state is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Code or state not provided")
    
    # print('provided state: ', state)
    # print('session state: ', request.session.get('oauth2_state'))

    client = AsyncOAuth2Client(
        client_id=OAUTH2_CLIENT_ID,
        client_secret=OAUTH2_CLIENT_SECRET,
        state=request.session.get('oauth2_state'),
        redirect_uri=OAUTH2_REDIRECT_URI)

    try:
        token = await client.fetch_token(TOKEN_URL, authorization_response=str(request.url))
    except Exception as e:
        return "Not Authorized"
    request.session['oauth2_token'] = token

    external_url = URL(FRONT_URI)
    #external_url = external_url.include_query_params(token=token['access_token'], state=request.session.get('oauth2_state'))

    response = RedirectResponse(url=str(external_url), status_code=301)
    response.set_cookie(key="token", value=json.dumps(token), httponly=True, samesite='lax', secure=True, domain=secret.DOMAIN)
    response.set_cookie(key="state", value=str(request.session.get('oauth2_state')), httponly=True, samesite='lax', secure=True, domain=secret.DOMAIN)
    response.set_cookie(key="auth", value="True", httponly=False, samesite='lax', secure=True, domain=secret.DOMAIN)


    await utils.FetchDiscordProfile(state, token)

    return response

@router.get('/discord/user', response_model=schemas.User)
async def user(request: Request):
    state, token = utils.getCookies(request)
    if not state or not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="state or token not provided")

    db = SessionLocal()
    db_user = crud.get_user_by_token(db=db, access_token=token['access_token'])
    db.close()

    if db_user:
        return db_user
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user not found")

@router.get('/discord/user/update', response_model=schemas.User)
async def user_update(request: Request):
    state, token = utils.getCookies(request)
    if not state or not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="state or token not provided")
    
    db = SessionLocal()
    db_user = crud.get_user_by_token(db=db, access_token=token['access_token'])
    db.close()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user not found")
    
    data, new_token = await utils.FetchDiscordProfile(state, token)
    if not new_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=data)

    response = JSONResponse(content=json.loads(data.model_dump_json()))
    if new_token:
        response.set_cookie(key="token", value=json.dumps(new_token), httponly=True, samesite='none', secure=True, domain="localhost")
    
    return response

@router.get('/logout')
async def logout(request: Request):
    external_url = URL(FRONT_URI)
    response = RedirectResponse(url=str(external_url), status_code=301)
    response.delete_cookie("token")
    response.delete_cookie("state")
    response.delete_cookie("auth")
    return response