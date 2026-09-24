# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.9
SHELL ["/bin/bash", "-c"]
WORKDIR /backend
# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir numpy
RUN pip install --no-cache-dir --upgrade -r /backend/requirements.txt

COPY ./src ./src

# Default container run.
EXPOSE 8080
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
