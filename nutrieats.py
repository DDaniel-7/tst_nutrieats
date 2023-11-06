from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import json

app = FastAPI()

with open('data.json', 'r') as file:
    data = json.load(file)

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

@app.get("/get_menu")
def get_menu():
    return data["menu"]


@app.get("/get_user")
def get_user():
    return data["user"]


@app.put("/update_menu")
async def update_menu(id_menu: int, nama_menu: str, kalori: int, target: str):
    for menu in data["menu"]:
        if menu["id_menu"] == id_menu:
            menu["nama_menu"] = nama_menu
            menu["kalori"] = kalori
            menu["target"] = target
            with open('data.json', 'w') as outfile:
                json.dump(data, outfile, indent=4)
            return {"message": "Menu updated successfully"}
    return {"error": "Menu not found"}


@app.delete("/delete_menu")
async def delete_menu(id_menu: int):
    for menu in data["menu"]:
        if menu["id_menu"] == id_menu:
            data["menu"].remove(menu)
            with open('data.json', 'w') as outfile:
                json.dump(data, outfile, indent=4)
            return {"message": "Menu deleted successfully"}
    return {"error": "Menu not found"}


@app.post("/add_menu")
async def add_menu(id_menu: int, nama_menu: str, kalori: int, target: str):
    menu_ids = {menu["id_menu"] for menu in data["menu"]}
    if id_menu in menu_ids:
        raise HTTPException(status_code=400, detail="ID already exists")
    new_menu = {"id_menu": id_menu, "nama_menu": nama_menu, "kalori": kalori, "target": target}
    data["menu"].append(new_menu)
    with open('data.json', 'w') as outfile:
        json.dump(data, outfile, indent=4)
    return {"message": "Menu added successfully"}


@app.post("/add_user")
async def add_user(id_user: int, nama_user: str, umur_user: int, target: str):
    user_ids = {user["id_user"] for user in data["user"]}
    if id_user in user_ids:
        raise HTTPException(status_code=400, detail="ID already exists")
    new_user = {"id_user": id_user, "nama_user": nama_user, "umur_user": umur_user, "target": target}
    data["user"].append(new_user)
    with open('data.json', 'w') as outfile:
        json.dump(data, outfile, indent=4)
    return {"message": "User added successfully"}

@app.get("/get_recommendation")
def get_recommendation(id_user: int):
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