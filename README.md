# II3160 Teknologi Sistem Terintegrasi 

Dwicakra Danielle / 18221092

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
```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

# run uvicorn 
```
uvicorn nutrieats:app --reload
```

# Docker build
```
docker image build --tag demo-app-image .
```
# Docker run
```
docker container run --publish 8000:8000 --name demo-app-container demo-app-image
```

# Containerize Docker to Azure
```
docker login deployappimage.azurecr.io/daniel:latest
```

# Build image in azure
```
docker build -t deployappimage.azurecr.io/deployimage:latest .
```

# Push image in Azure
```
docker push deployappimage.azurecr.io/deployimage:latest
```





