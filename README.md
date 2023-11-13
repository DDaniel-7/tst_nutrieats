# II3160 Teknologi Sistem Terintegrasi 

Dwicakra Danielle / 18221092
Testing API dapat dilakukan dengan dns berikut:
dnsnutrieatsfilter.ffb6hxbfa2d7fmd5.southeastasia.azurecontainer.io/docs

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





