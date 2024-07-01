import discord
import json

import secret

from authlib.integrations.httpx_client import AsyncOAuth2Client

from database import crud, schemas 
from database.database import SessionLocal

def create_user_from_member(member: discord.Member):
    roles = []
    admin = False
    for role in member.roles:
        role_new = str(role.id)
        if role.name == 'General' or role.name == 'Warlord':
            admin = True
        roles.append(role_new)

    db_user = {
        'id': str(member.id),
        'username': member.name,
        'global_name': getattr(member, 'global_name', None) or None,
        'avatar': getattr(member.avatar, 'key', None) or None,
        'member': True,
        'admin': admin,
        'nickname': member.display_name,
        'joined_at': member.joined_at,
        'roles': roles,
        'connection_time': 0,
        'access_token': None,
        'expires_in': None,
        'expires_at': None
    }

    return db_user

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

async def FetchDiscordProfile(state, token):
    print('provided state: ', state)
    print('provided token: ', token)
    if not state or not token:
        print('fetch failed, state or token missing')
        return {'error': 'state or token missing'}, False
    client = AsyncOAuth2Client(
        client_id=secret.OAUTH2_CLIENT_ID,
        client_secret=secret.OAUTH2_CLIENT_SECRET,
        redirect_uri=secret.OAUTH2_REDIRECT_URI,
        state=state,
        token=token,
        token_endpoint='https://discord.com/api/oauth2/token')
    
    print("new_token: ", client.token)

    user_response = await client.get('https://discord.com/api' + '/users/@me')
    seduction_response = await client.get('https://discord.com/api' + '/users/@me/guilds/' + str(secret.GUILD_ID) + '/member')

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
        'expires_at': token['expires_at'],
        'member': member,
        'admin': isadmin,
        'nickname': seduction.get('nick', None),
        'joined_at': seduction.get('joined_at', None),
        'roles': seduction.get('roles', None)
    }
    
    db_user_old = crud.get_user(db=db, user_id=user['id'])
    if db_user_old:
        db_user['connection_time'] = db_user_old.connection_time
        crud.update_user(db=db, user_id=user['id'], user=schemas.UserCreate(**db_user))
    else:
        db_user['connection_time'] = 0
        crud.create_user(db=db, user=schemas.UserCreate(**db_user))

    db.close()
    return schemas.User(**db_user), client.token