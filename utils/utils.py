import discord
import json
from database import schemas

def create_user_from_member(member: discord.Member):
    roles = []
    admin = False
    for role in member.roles:
        role_new = role.id
        if role.name == 'General' or role.name == 'Warlord':
            admin = True
        roles.append(role_new)

    db_user: schemas.UserCreate = {
        'id': member.id,
        'username': member.name,
        'global_name': member.global_name,
        'avatar': member.avatar.key,
        'member': True,
        'admin': admin,
        'nickname': member.display_name,
        'joined_at': member.joined_at,
        'roles': roles
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