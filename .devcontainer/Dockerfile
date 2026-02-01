FROM mcr.microsoft.com/devcontainers/python:3.14

# Install system dependencies here if needed.
# RUN apt-get update && apt-get install -y <packages>

# Install Poetry
ENV POETRY_HOME=/opt/poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
  && ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry
