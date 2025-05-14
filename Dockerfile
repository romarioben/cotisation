#Use the official python runtime image
FROM python:3.12-slim

# Create the app directory
RUN mkdir /app

# Set the working directory inside the container
WORKDIR /app

# Set environnement variables
#Prevent Python from writting pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1

# Prevent Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

#Upgrade pip
RUN pip install --upgrade pip

# Copy the django project and install dependencies
COPY requirements.txt /app/

# Run this command to install all dependencies
RUN pip install --no-cache-dir -r requirements.txt


# Copy the django project to the container
COPY . /app/

RUN chmod a+x /app/entrypoint.sh

#Entry point for collecting static files before starting the server
ENTRYPOINT [ "/app/entrypoint.sh" ]

# Set the command to run our web service using Gunicorn binding it to 0.0.0.0 and the port
CMD gunicorn printLAB.wsgi:application --bind 0.0.0.0:8000

# Inform docker that the container listens on the  specified network port at the  runtime

EXPOSE 8000
