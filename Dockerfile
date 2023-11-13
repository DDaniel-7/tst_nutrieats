# Use the official Python image from the Docker Hub
FROM python:3

# Set the working directory inside the container
ADD nutrieats.py .

# Copy the current directory contents into the container at /app
COPY . /fastapi
WORKDIR /fastapi

# Install any necessary dependencies
RUN pip install fastapi uvicorn passlib bcrypt jwt pyjwt python-multipart

# Command to run the FastAPI server when the container starts
CMD ["uvicorn", "nutrieats:app", "--host", "0.0.0.0", "--port", "80"]
