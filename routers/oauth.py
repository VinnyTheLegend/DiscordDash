import os
import json

from fastapi import APIRouter, HTTPException, Request, status, Response
from fastapi.responses import RedirectResponse, JSONResponse

from starlette.datastructures import URL

from authlib.integrations.httpx_client import AsyncOAuth2Client

import secret

OAUTH2_CLIENT_ID = secret.OAUTH2_CLIENT_ID
OAUTH2_CLIENT_SECRET = secret.OAUTH2_CLIENT_SECRET
OAUTH2_REDIRECT_URI = secret.OAUTH2_REDIRECT_URI

GUILD_ID = secret.GUILD_ID

FRONT_URI = secret.FRONT_URI

API_BASE_URL = 'https://discord.com/api'
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'
SCOPE = 'identify guilds guilds.members.read'

if 'http://' in OAUTH2_REDIRECT_URI:
    os.environ['AUTHLIB_INSECURE_TRANSPORT'] = 'true'


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
    guilds_response = await client.get(API_BASE_URL + '/users/@me/guilds')
    seduction_response = await client.get(API_BASE_URL + '/users/@me/guilds/' + GUILD_ID + '/member')

    print('user: ' + str(user_response.status_code))
    print('guilds: ' + str(guilds_response.status_code))
    print('seduction: ' + str(seduction_response.status_code))
    if user_response.status_code !=200 or guilds_response.status_code !=200 or seduction_response.status_code != 200:
        return {'error': 'discord @me request failed'}, False

    user = user_response.json()
    guilds = guilds_response.json()
    seduction = seduction_response.json()

    data = {"user": user, "guilds": guilds}

    if [item for item in guilds if item.get('id') == secret.GUILD_ID]:
        data["seduction"] = seduction
        if "roles" in seduction:
            if "591686220996935691" in seduction["roles"]:
                isadmin = True
            else:
                isadmin = False
    else:
        isadmin = False
        
    data['isadmin'] = isadmin

    return data, client.token

async def IsAdmin(request):
    state, token = getCookies(request)
    if not state or not token:
        return False
    client = AsyncOAuth2Client(
        client_id=OAUTH2_CLIENT_ID,
        client_secret=OAUTH2_CLIENT_SECRET,
        redirect_uri=OAUTH2_REDIRECT_URI,
        state=state,
        token=token,
        token_endpoint=TOKEN_URL)
    
    seduction = await client.get(API_BASE_URL + '/users/@me/guilds/' + GUILD_ID + '/member')

    if "591686220996935691" in seduction.json()["roles"]:
        return True
    else:
        return False

@router.get('/discord/me')
async def me(request: Request):
    state, token = getCookies(request)
    if not state or not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="state or token not provided")

    data, token = await FetchDiscordProfile(request)

    response = JSONResponse(content=data)
    if token:
        response.set_cookie(key="token", value=json.dumps(token), httponly=True, samesite='none', secure=True, domain="localhost")
    
    return response

@router.get('/isadmin')
async def test(request: Request):
    state, token = getCookies(request)
    if not state or not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="state or token not provided")
    return {"is admin": await IsAdmin(request)}