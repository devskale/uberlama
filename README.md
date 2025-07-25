# Ollama Crowd-Funded Server

Welcome to the **Ollama Crowd-Funded Server**! This server allows you to communicate with Ollama models using official JavaScript or Python clients. The servers are generously provided by individuals who contribute their resources.

## Table of Contents

- [Using the Ollama Server](#using-the-ollama-server)
- [WebSocket Client](#websocket-client)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Using the Ollama Server

To use the Ollama server, simply utilize the original client with the provided URL. Below is an example of how to use the Ollama client in Python:

```python
from ollama import Client

client = Client(
    host="https://ollama.molodetz.nl"
)

messages = []

def chat(message):
    if message:
        messages.append({'role': 'user', 'content': message})
    content = ''
    for response in client.chat(model='qwen2.5-coder:0.5b', messages=messages, stream=True):
        content += response.message.content
        print(response.message.content, end='', flush=True)
    messages.append({'role': 'assistant', 'content': content})
    print("")

while True:
    message = input("You: ")
    chat(message)
```

## WebSocket Client

The `client.py` script is an asynchronous WebSocket client for the Ollama API. It connects to the Ollama server, fetches available models, and listens for messages.

### Features

- Asynchronous WebSocket connections using `aiohttp`.
- Fetches available models from the Ollama API.
- Logs received data and errors.
- Supports concurrent WebSocket connections.

### Installation

To run the WebSocket client, ensure you have Python 3.7 or higher installed. You can install the required dependencies using pip:

```bash
pip install aiohttp
```

### Usage

You can run the WebSocket client with the following command:

```bash
python client.py --concurrency <number_of_connections> --ollama_url <ollama_api_url>
```

- `--concurrency`: Number of concurrent WebSocket connections (default: 4).
- `--ollama_url`: Ollama API URL (default: `https://localhost:11434`).

### Example

To run the client with the default settings:

```bash
python client.py
```

## Contributing

Contributions are welcome! If you would like to contribute to the project, please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.