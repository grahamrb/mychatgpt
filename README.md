# MyChatGPT

## Description

This is a simple implementation of a chat interface using Azure OpenAI APIs and Python (Flask).
The aim of the implementation is to keep it as simple and self-contained as possible to allow easy deployment of a private GPT chatbot.

Websockets are used to allow for streaming of response for a more "chat-like" experience. The base implementation for the sockets and chat UI is based on https://github.com/miguelgrinberg/Flask-SocketIO/blob/main/example/app.py

## Configuration

Ensure the following three environment variables are set:

- `OPENAI_API_BASE`: The base of your Azure OpenAI API
- `OPENAI_API_KEY`: Your Azure OpenAI API key
- `OPENAI_DEPLOYMENT_NAME`: The deployment name of your Azure OpenAI instance

All three of the above are available in the Azure Portal.

