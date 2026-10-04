# Base build
FROM python:3.11-slim AS build
WORKDIR /bookmarks_app

# Install the necessary python libraries and packages
RUN pip install --target=/bookmarks_app/libraries fastapi "fastapi[standard]" psycopg2-binary
COPY main.py ./

# We replace the previous stage with a runtime stage
FROM python:3.11-slim
WORKDIR /bookmarks_app
RUN apt-get update && apt-get upgrade -y && pip install --upgrade pip setuptools "wheel>=0.46.2"
COPY --from=build /bookmarks_app /bookmarks_app

ENV PYTHONPATH=/bookmarks_app/libraries
USER 65530
EXPOSE 80 8080
CMD [ "python3", "-m", "fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8080" ]