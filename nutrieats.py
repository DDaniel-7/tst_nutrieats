from fastapi import FastAPI, HTTPException, Depends, status, APIRouter
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from datetime import datetime
import json
import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.hash import bcrypt

with open('data.json', 'r') as file:
    data = json.load(file)

menu = APIRouter(tags=["menu"],)
user = APIRouter(tags=["user"],)
auth = APIRouter(tags=["auth"],)
recomendation = APIRouter(tags=["recommendation"],)

class User(BaseModel):
    id_user: int
    nama_user: str
    umur_user: int
    target: str

class Recommendation(BaseModel):
    id_user: int
    id_menu: int
    date: str

class Menu(BaseModel):
    id_menu: int
    nama_menu: str
    kalori: int
    target: str

class signin_user:
    def __init__(self, id, username, pass_hash):
        self.id = id
        self.username = username
        self.pass_hash = pass_hash

    def verify_password(self, password):
        return bcrypt.verify(password, self.pass_hash)

def write_data(data):
    with open("data.json", "w") as write_file:
        json.dump(data, write_file, indent=4)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')
app = FastAPI()
JWT_SECRET = 'myjwtsecret'
ALGORITHM = 'HS256'

def get_user_by_username(username):
    for desain_user in data['signin_user']:
        if desain_user['username'] == username:
            return desain_user
    return None

def authenticate_user(username: str, password: str):
    user_data = get_user_by_username(username)
    if not user_data:
        return None

    user = signin_user(id=user_data['id'], username=user_data['username'], pass_hash=user_data['pass_hash'])

    if not user.verify_password(password):
        return None

    return user


@auth.post('/token')
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Invalid username or password'
        )

    token = jwt.encode({'id': user.id, 'username': user.username}, JWT_SECRET, algorithm=ALGORITHM)

    return {'access_token': token, 'token_type': 'bearer'}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user = get_user_by_username(payload.get('username'))
        return signin_user(id=user['id'], username=user['username'], pass_hash=user['pass_hash'])
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Invalid username or password'
        )

@auth.post('/signin_user')
async def create_user(username: str, password: str):
    last_user_id = data['signin_user'][-1]['id'] if data['signin_user'] else 0
    user_id = last_user_id + 1
    user = jsonable_encoder(signin_user(id=user_id, username=username, pass_hash=bcrypt.hash(password)))
    data['signin_user'].append(user)
    write_data(data)
    return {'message': 'User created successfully'}

@auth.get('/signin_user/me')
async def get_user(user: signin_user = Depends(get_current_user)):
    return {'id': user.id, 'username': user.username}

@menu.get("/get_menu")
def get_menu(user: signin_user = Depends(get_current_user)):
    return data["menu"]


@user.get("/get_user")
def get_user(user: signin_user = Depends(get_current_user)):
    return data["user"]


@menu.put("/update_menu")
async def update_menu(id_menu: int, nama_menu: str, kalori: int, target: str, user: signin_user = Depends(get_current_user)):
    for menu in data["menu"]:
        if menu["id_menu"] == id_menu:
            menu["nama_menu"] = nama_menu
            menu["kalori"] = kalori
            menu["target"] = target
            with open('data.json', 'w') as outfile:
                json.dump(data, outfile, indent=4)
            return {"message": "Menu updated successfully"}
    return {"error": "Menu not found"}


@menu.delete("/delete_menu")
async def delete_menu(id_menu: int, user: signin_user = Depends(get_current_user)):
    for menu in data["menu"]:
        if menu["id_menu"] == id_menu:
            data["menu"].remove(menu)
            with open('data.json', 'w') as outfile:
                json.dump(data, outfile, indent=4)
            return {"message": "Menu deleted successfully"}
    return {"error": "Menu not found"}


@menu.post("/add_menu")
async def add_menu(id_menu: int, nama_menu: str, kalori: int, target: str, user: signin_user = Depends(get_current_user)):
    menu_ids = {menu["id_menu"] for menu in data["menu"]}
    if id_menu in menu_ids:
        raise HTTPException(status_code=400, detail="ID already exists")
    new_menu = {"id_menu": id_menu, "nama_menu": nama_menu, "kalori": kalori, "target": target}
    data["menu"].append(new_menu)
    with open('data.json', 'w') as outfile:
        json.dump(data, outfile, indent=4)
    return {"message": "Menu added successfully"}


@user.post("/add_user")
async def add_user(id_user: int, nama_user: str, umur_user: int, target: str, user: signin_user = Depends(get_current_user)):
    user_ids = {user["id_user"] for user in data["user"]}
    if id_user in user_ids:
        raise HTTPException(status_code=400, detail="ID already exists")
    new_user = {"id_user": id_user, "nama_user": nama_user, "umur_user": umur_user, "target": target}
    data["user"].append(new_user)
    with open('data.json', 'w') as outfile:
        json.dump(data, outfile, indent=4)
    return {"message": "User added successfully"}

@recomendation.get("/get_recommendation")
def get_recommendation(id_user: int, user: signin_user = Depends(get_current_user)):
    user_target = None
    for user in data["user"]:
        if user["id_user"] == id_user:
            user_target = user["target"]
            break
    if user_target is None:
        return []

    menu_ids = []
    recommended_menus = set()
    for menu in data["menu"]:
        if menu["target"] == user_target:
            menu_ids.append(menu["id_menu"])
            recommended_menus.add(menu["nama_menu"])

    for rec in data["recomendation"]:
        if rec["id_user"] == id_user and rec["id_menu"] in menu_ids:
            for menu in data["menu"]:
                if menu["id_menu"] == rec["id_menu"]:
                    recommended_menus.add(menu["nama_menu"])

    new_recommendation_id = max(rec["id"] for rec in data["recomendation"]) + 1 if data["recomendation"] else 1
    new_recommendations = [{"id": new_recommendation_id + i, "id_user": id_user, "id_menu": menu_id, "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")} for i, menu_id in enumerate(menu_ids)]
    data["recomendation"].extend(new_recommendations)
    with open('data.json', 'w') as outfile:
        json.dump(data, outfile, indent=4)

    return list(recommended_menus)

app.include_router(menu)
app.include_router(user)
app.include_router(auth)
app.include_router(recomendation)
