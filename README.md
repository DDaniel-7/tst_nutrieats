# II3160 Teknologi Sistem Terintegrasi 

Dwicakra Danielle / 18221092

Testing API dapat dilakukan dengan dns berikut:

integrationdns.bdh6crgwhtdwaqan.southeastasia.azurecontainer.io/docs

Sebelum menjalankan program maka ada beberapa yang perlu di install untuk menjalankan API
# Install fastapi
```
python -m pip install fastapi     
```

# Install uvicorn
```
python -m pip install uvicorn     
```

# Install virtual environrment
```
python -m pip install virtualenv      
```

# Activate virtual environrment
```
venv\Scripts\Activate.ps1 
```
OR
```
.\venv\Scripts\activate
```

# Setting up before run uvicorn 
Dilakukan untuk prevent error yang terjadi
```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

# run uvicorn 
```
uvicorn nutrieats:app --reload
```





