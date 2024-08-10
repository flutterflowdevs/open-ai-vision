# Use a Python 3.12.3-slim-buster image as the base
FROM python:3.12.3

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port your Flask app will listen on
EXPOSE 5000

# Command to run the Flask app
CMD ["python", "app.py"]
