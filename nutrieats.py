from fastapi import FastAPI, HTTPException, Depends, status, APIRouter
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from datetime import datetime
import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.hash import bcrypt
import requests
from pymongo import MongoClient

client = MongoClient('mongodb+srv://18221092:Sn12345@cluster0.madmsqj.mongodb.net/?retryWrites=true&w=majority')
db = client["data"]
collection = db["API"]
data = collection.find_one({})

integratedToken = ''

auth = APIRouter(tags=["auth"],)
menu = APIRouter(tags=["menu"],)
user = APIRouter(tags=["user"],)
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

class signin_admin:
    def __init__(self, id, username, pass_hash):
        self.id = id
        self.username = username
        self.pass_hash = pass_hash

    def verify_password(self, password):
        return bcrypt.verify(password, self.pass_hash)

def write_data(data):
    collection.replace_one({}, data, upsert=True)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')
app = FastAPI()
JWT_SECRET = 'myjwtsecret'
ALGORITHM = 'HS256'

def get_admin_by_username(username):
    for desain_user in data['signin_admin']:
        if desain_user['username'] == username:
            return desain_user
    return None

def authenticate_admin(username: str, password: str):
    admin_data = get_admin_by_username(username)
    if not admin_data:
        return None

    admin = signin_admin(id=admin_data['id'], username=admin_data['username'], pass_hash=admin_data['pass_hash'])

    if not admin.verify_password(password):
        return None

    return admin


@auth.post('/token')
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    global integratedToken
    admin = authenticate_admin(form_data.username, form_data.password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Invalid username or password'
        )
    url = 'https://bevbuddy.up.railway.app/login'
    data = {
        'username': form_data.username,
        'password': form_data.password
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        try:
            result = response.json()
            global integratedToken
            integratedToken = result.get('token')
            token = jwt.encode({'id': admin.id, 'username': admin.username}, JWT_SECRET, algorithm=ALGORITHM)
        except ValueError as e:
            print("Invalid JSON format in response:", response.text)
            return {'Error': 'Invalid JSON format in response'}
        return {'access_token': token, 'token_type': 'bearer', 'integrasiToken' : integratedToken}
    else:
        return {'Error': response.status_code, 'Detail': response.text}

async def get_current_admin(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        admin = get_admin_by_username(payload.get('username'))
        return signin_admin(id=admin['id'], username=admin['username'], pass_hash=admin['pass_hash'])
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Invalid username or password'
        )

@auth.post('/signin_admin')
async def create_user(username: str,fullname: str, password: str, email : str):
    for existing_user in data['signin_admin']:
        if existing_user['username'] == username:
            # Username already exists, return an appropriate response
            return {"error": "Username already taken"}
    last_admin_id = data['signin_admin'][-1]['id'] if data['signin_admin'] else 0
    admin_id = last_admin_id + 1
    user = jsonable_encoder(signin_admin(id=admin_id, username=username, pass_hash=bcrypt.hash(password)))
    data['signin_admin'].append(user)
    url = 'https://bevbuddy.up.railway.app/register'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    admin_data = {
        "username": username,
        "fullname": fullname,
        "email": email+"@gmail.com",
        "password": password,
        "role": "customer",
        "token": "tokendaniel"
    }
    response = requests.post(url, headers=headers, json=admin_data)
    write_data(data)
    return {"username" : username, "password" : password,"email": email+"@gmail.com", "integratedRegister" : response.json()}
    

@auth.get('/current_admin')
async def get_admin(admin: signin_admin = Depends(get_current_admin)):
    return {'id': admin.id, 'username': admin.username}

@menu.get("/menu")
def get_menu(admin: signin_admin = Depends(get_current_admin)):
    return data["menu"]


@user.get("/user")
def get_user(admin: signin_admin = Depends(get_current_admin)):
    return data["user"]


@menu.put("/menu")
async def update_menu(id_menu: int, nama_menu: str, kalori: int, target: str, admin: signin_admin = Depends(get_current_admin)):
    for menu in data["menu"]:
        if menu["id_menu"] == id_menu:
            menu["nama_menu"] = nama_menu
            menu["kalori"] = kalori
            menu["target"] = target
            write_data(data)
            return {"message": "Menu updated successfully"}
    return {"error": "Menu not found"}


@menu.delete("/menu")
async def delete_menu(id_menu: int, admin: signin_admin = Depends(get_current_admin)):
    for menu in data["menu"]:
        if menu["id_menu"] == id_menu:
            data["menu"].remove(menu)
            write_data(data)
            return {"message": "Menu deleted successfully"}
    return {"error": "Menu not found"}


@menu.post("/menu")
async def add_menu(id_menu: int, nama_menu: str, kalori: int, target: str, admin: signin_admin = Depends(get_current_admin)):
    menu_ids = {menu["id_menu"] for menu in data["menu"]}
    if id_menu in menu_ids:
        raise HTTPException(status_code=400, detail="ID already exists")
    new_menu = {"id_menu": id_menu, "nama_menu": nama_menu, "kalori": kalori, "target": target}
    data["menu"].append(new_menu)
    write_data(data)
    return {"message": "Menu added successfully"}


@user.post("/user")
async def add_user(id_user: int, nama_user: str, umur_user: int, target: str, admin: signin_admin = Depends(get_current_admin)):
    user_ids = {user["id_user"] for user in data["user"]}
    if id_user in user_ids:
        raise HTTPException(status_code=400, detail="ID already exists")
    new_user = {"id_user": id_user, "nama_user": nama_user, "umur_user": umur_user, "target": target}
    data["user"].append(new_user)
    write_data(data)
    return {"message": "User added successfully"}

@user.delete("/user")
async def delete_user(id_user: int, admin: signin_admin = Depends(get_current_admin)):
    for user in data["user"]:
        if user["id_user"] == id_user:
            data["user"].remove(user)
            write_data(data)
            return {"message": "Menu deleted successfully"}
    return {"error": "Menu not found"}

@recomendation.get("/food_Recommendation")
def food_recommendation(id_user: int, admin: signin_admin = Depends(get_current_admin)):
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
    return list(recommended_menus)


@app.post("/recommendations", tags = ["Integrations"])      
async def recommendations(activity: str, age: int, gender: str, height: int, max_rec : int, weather : str, weight: int, admin: signin_admin = Depends(get_current_admin)):
    global integratedToken
    base_url = "https://bevbuddy.up.railway.app/recommendations"
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {integratedToken}'
    }
    form_data = {
        "activity": activity,
        "age": age,
        "gender": gender,
        "height": height,
        "max_rec": max_rec,
        "weather": weather,
        "weight": weight
    }
    response = requests.post(base_url, headers=headers, json=form_data)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return {'Error': response.status_code, 'Detail': response.text}

app.include_router(auth)
app.include_router(menu)
app.include_router(user)
app.include_router(recomendation)
