import os
import json
import secret

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import RedirectResponse, JSONResponse

from starlette.datastructures import URL

from authlib.integrations.httpx_client import AsyncOAuth2Client

from database import crud, models, schemas 
from database.database import SessionLocal, engine

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

def getCookies(request):
    state = request.cookies.get('state')
    token = request.cookies.get('token')

    if state is None:
        state = False

    if token is None:
        token = False
    else:
        token = json.loads(token)
    
    return state, token

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
async def callback(request: Request, code: str = None, state: str = None):
    if code is None or state is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Code or state not provided")
    
    print('provided state: ', state)
    print('session state: ', request.session.get('oauth2_state'))

    client = AsyncOAuth2Client(
        client_id=OAUTH2_CLIENT_ID,
        client_secret=OAUTH2_CLIENT_SECRET,
        state=request.session.get('oauth2_state'),
        redirect_uri=OAUTH2_REDIRECT_URI)

    token = await client.fetch_token(TOKEN_URL, authorization_response=str(request.url))
    request.session['oauth2_token'] = token

    external_url = URL(FRONT_URI)
    #external_url = external_url.include_query_params(token=token['access_token'], state=request.session.get('oauth2_state'))

    response = RedirectResponse(url=str(external_url))
    response.set_cookie(key="token", value=json.dumps(token), httponly=True, samesite='none', secure=True, domain="localhost")
    response.set_cookie(key="state", value=request.session.get('oauth2_state'), httponly=True, samesite='none', secure=True, domain="localhost")


    return response

@router.get("/discord/read-cookie")
async def read_cookie(request: Request):
    state, token = getCookies(request)
    if not token or not state:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="state or token not provided")
    return {"state": state, "token": token}


async def FetchDiscordProfile(request):
    state, token = getCookies(request)
    if not state or not token:
        return {'error': 'state or token missing'}, False
    client = AsyncOAuth2Client(
        client_id=OAUTH2_CLIENT_ID,
        client_secret=OAUTH2_CLIENT_SECRET,
        redirect_uri=OAUTH2_REDIRECT_URI,
        state=state,
        token=token,
        token_endpoint=TOKEN_URL)
    
    print("new_token: ", client.token)

    user_response = await client.get(API_BASE_URL + '/users/@me')
    seduction_response = await client.get(API_BASE_URL + '/users/@me/guilds/' + GUILD_ID + '/member')

    print('user: ' + str(user_response.status_code))
    print('seduction: ' + str(seduction_response.status_code))

    user = user_response.json()
    seduction = seduction_response.json()

    isadmin = False
    member = False

    if user_response.status_code !=200:
        return {'error': user}, False

    if seduction_response.status_code == 200:
        member = True
        if "roles" in seduction:
            if "591686220996935691" in seduction["roles"]:
                isadmin = True
        
    db = SessionLocal()

    db_user = {
        'id': user['id'],
        'username': user['username'],
        'global_name': user['global_name'],
        'avatar': user['avatar'],
        'access_token': token['access_token'],
        'expires_in': token['expires_in'],
        'refresh_token': token['refresh_token'],
        'expires_at': token['expires_at'],
        'member': member,
        'admin': isadmin,
        'nickname': seduction.get('nick', None),
        'joined_at': seduction.get('joined_at', None),
        'roles': seduction.get('roles', None)
    }
    
    db_user_old = crud.get_user(db=db, user_id=user['id'])
    if db_user_old:
        crud.update_user(db=db, user_id=user['id'], user=schemas.UserCreate(**db_user))
    else:
        crud.create_user(db=db, user=schemas.UserCreate(**db_user))

    db.close()
    return db_user, client.token

@router.get('/discord/me')
async def me(request: Request):
    state, token = getCookies(request)
    if not state or not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="state or token not provided")

    data, new_token = await FetchDiscordProfile(request)

    if not new_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=data)

    response = JSONResponse(content=data)
    if new_token:
        response.set_cookie(key="token", value=json.dumps(new_token), httponly=True, samesite='none', secure=True, domain="localhost")
    
    return response