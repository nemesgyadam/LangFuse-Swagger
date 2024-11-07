# Use an official Python runtime as a parent image
FROM python:3.12-slim


# Set the working directory in the container
WORKDIR /app

# Install dependencies separately to leverage Docker caching
COPY requirements.txt /app/
RUN pip install --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app

EXPOSE 8000

ENTRYPOINT ["python", "main.py"]
