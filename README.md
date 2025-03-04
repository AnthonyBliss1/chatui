# Chat Interface

A simple chat ui that allows you to interact with various AI models including OpenAI's GPT models and Anthropic's Claude models.

## Features

- Clean, terminal-based UI built with Textual
- Support for multiple AI models:
  - OpenAI: GPT-4o, o1-preview, o1-mini, o3-mini
  - Anthropic: Claude 3.7 Sonnet
- Easy model switching during chat, click model name to switch
- Streaming responses

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/chat-interface.git
   cd chat-interface
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your API keys:
   ```
   cp .env.template .env
   ```
   Then edit the `.env` file and add your API keys.

## Usage

Run the application:

python main.py


### Controls
- Type your message and press Enter or click Send to submit
- Click on the model name in the input field to switch between available models
- Press Ctrl+Q to quit

### Add Models
Follow the defined format and add new models to models.py