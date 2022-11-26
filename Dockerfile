FROM python:3.10.2

# Copy requirements to the app root
COPY requirements/ ./src/requirements/

# Set working directory for the purpose of this Dockerfile
WORKDIR /src

# Update Pip
RUN pip install pip==22.3.1

# Install the dependencies
RUN pip install -r requirements/deploy.pip

COPY . .

CMD ["sh","-c","cd src && gunicorn -b 0.0.0.0:80 app:application --timeout 0"]
