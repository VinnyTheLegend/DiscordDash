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
    if request.cookies.get('my_cookie'):
        return {"state": request.cookies.get('state'), "token": request.cookies.get('token')}
    else:
        return {"message": "No cookie found"}    


async def FetchDiscordProfile(request):
    print(request.cookies.get('state'))
    print(request.cookies.get('token'))
    state = request.cookies.get('state')
    token = json.loads(request.cookies.get('token'))
    client = AsyncOAuth2Client(
        client_id=OAUTH2_CLIENT_ID,
        client_secret=OAUTH2_CLIENT_SECRET,
        redirect_uri=OAUTH2_REDIRECT_URI,
        state=state,
        token=token,
        token_endpoint=TOKEN_URL)
    
    print("new_token: ", client.token)

    user = await client.get(API_BASE_URL + '/users/@me')
    guilds = await client.get(API_BASE_URL + '/users/@me/guilds')
    seduction = await client.get(API_BASE_URL + '/users/@me/guilds/' + GUILD_ID + '/member')

    if "591686220996935691" in seduction.json()["roles"]:
        isadmin = True
    else:
        isadmin = False

    data = {"isadmin": isadmin, "user": user.json(), "seduction": seduction.json(), "guilds": guilds.json()}

    return data, client.token

async def IsAdmin(request):
    state = request.cookies.get('state')
    token = json.loads(request.cookies.get('token'))
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
    data, token = await FetchDiscordProfile(request)

    response = JSONResponse(content=data)
    response.set_cookie(key="token", value=json.dumps(token), httponly=True, samesite='none', secure=True, domain="localhost")
    response.set_cookie(key="test", value="me test", httponly=True, samesite='none', secure=True, domain="localhost")
    
    return response

@router.get('/test')
async def test(request: Request):
    return {"message": await IsAdmin(request)}
    