import os
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.containers import Horizontal, Vertical, ScrollableContainer
from textual.widgets import Static, Button, Input, Markdown, Tabs, Tab, Select, LoadingIndicator
from textual.binding import Binding
from textual.worker import Worker, get_current_worker
from textual.errors import NoWidget
from chat.chat import get_streaming_response
from typing import List, Dict
from chat.models import AVAILABLE_MODELS, DEFAULT_MODEL
from textual import events

class Message(Static):
    def __init__(self, content: str, is_user: bool = False) -> None:
        super().__init__()
        self.is_user = is_user
        self.content = content
        self.add_class("user-message" if is_user else "bot-message")

    def update(self, content: str) -> None:
        self.content = content
        self.refresh(layout=True)

    def render(self) -> str:
        try:
            available_width = self.size.width
        except NoWidget:
            available_width = 80
            
        content_width = max(20, available_width - 4)  # -4 for padding
        
        content_lines = []
        for line in self.content.split('\n'):
            while len(line) > content_width:
                split_point = line[:content_width].rfind(' ')
                if split_point == -1:
                    split_point = content_width
                content_lines.append(line[:split_point])
                line = line[split_point:].lstrip()
            content_lines.append(line)
        
        return '\n'.join(content_lines)

class ModelIndicator(Static):
    def __init__(self, model_name: str):
        super().__init__()
        self.model_name = model_name
        self.add_class("model-indicator")

    def render(self) -> str:
        return f"[{AVAILABLE_MODELS[self.model_name].display_name}]"

class BotMessage(Static):
    def __init__(self):
        super().__init__()
        self.add_class("bot-message")
        self.content = ""
        self.is_loading = True
        self.loading_frames = [
            "⣷",
            "⣯",
            "⣟",
            "⡿",
            "⢿",
            "⣻",
            "⣽",
            "⣾"
        ]
        self.frame_index = 0

    def on_mount(self) -> None:
        self.set_interval(0.1, self._animate_loading)

    def _animate_loading(self) -> None:
        if self.is_loading:
            self.frame_index = (self.frame_index + 1) % len(self.loading_frames)
            self.refresh()

    def render(self) -> str:
        if self.is_loading:
            return self.loading_frames[self.frame_index % len(self.loading_frames)]
        return self.content

    def update_content(self, content: str) -> None:
        self.content = content
        self.is_loading = False
        self.refresh(layout=True)

class ChatInterface(Screen):
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("enter", "submit", "Submit")
    ]

    def __init__(self) -> None:
        super().__init__()
        self.message_history: List[Dict[str, str]] = []
        
        available_models = []
        for key, model in AVAILABLE_MODELS.items():
            api_key_name = "OPENAI_API_KEY" if model.api_type == "openai" else "ANTHROPIC_API_KEY"
            if os.getenv(api_key_name):
                available_models.append(key)
        
        if not available_models:
            self.selected_model = DEFAULT_MODEL
        else:
            self.selected_model = available_models[0]

    def compose(self) -> ComposeResult:
        yield Vertical(
            ScrollableContainer(id="chat-messages"),
            Horizontal(
                Input(placeholder="Type your message...", id="chat-input"),
                Button("Send", id="send-button", variant="primary"),
                id="chat-input-container"
            ),
            id="chat-container"
        )

    def on_mount(self) -> None:
        input_widget = self.query_one("#chat-input", Input)
        self._update_placeholder(input_widget)

    def _update_placeholder(self, input_widget: Input) -> None:
        model_name = AVAILABLE_MODELS[self.selected_model].display_name
        input_widget.placeholder = f"[{model_name}] Type your message..."

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "send-button":
            await self.send_message()

    async def action_submit(self) -> None:
        await self.send_message()

    async def send_message(self) -> None:
        input_widget = self.query_one("#chat-input", Input)
        user_input = input_widget.value.strip()
        if not user_input:
            return

        input_widget.value = ""
        messages = self.query_one("#chat-messages")
        
        user_message = Message(user_input, is_user=True)
        messages.mount(user_message)
        messages.scroll_end(animate=False)
        self.message_history.append({"role": "user", "content": user_input})

        bot_message = BotMessage()
        messages.mount(bot_message)
        messages.scroll_end(animate=False)
        
        model_config = AVAILABLE_MODELS[self.selected_model]
        api_key = os.getenv("OPENAI_API_KEY" if model_config.api_type == "openai" else "ANTHROPIC_API_KEY")
        
        if not api_key:
            bot_message.update_content(f"Error: {model_config.api_type.upper()} API key not found.")
            messages.scroll_end(animate=False)
            return

        async def work() -> None:
            full_response = ""
            try:
                async for chunk in get_streaming_response(self.message_history, api_key, self.selected_model):
                    if chunk.startswith("Error:"):
                        bot_message.update_content(chunk)
                        break
                    full_response += chunk
                    bot_message.update_content(full_response)
                    messages.scroll_end(animate=False)
                    self.refresh()
                
                self.message_history.append({"role": "assistant", "content": full_response})
            except Exception as e:
                print(f"Worker error: {str(e)}")
                bot_message.update_content(f"Error: {str(e)}")

        self.run_worker(work, thread=False)

    def on_click(self, event: events.Click) -> None:
        if isinstance(event.control, Input) and event.control.id == "chat-input":
            input_widget = event.control
            click_x = event.x - input_widget.region.x
            
            model_name = AVAILABLE_MODELS[self.selected_model].display_name
            model_text_with_brackets = f"[{model_name}]"
            
            model_start = 1  # position after '['
            model_end = len(model_text_with_brackets) - 1  # position before ']'
            
            if model_start <= click_x <= model_end:
                # get available models with valid API keys
                available_models = []
                for key, model in AVAILABLE_MODELS.items():
                    api_key_name = "OPENAI_API_KEY" if model.api_type == "openai" else "ANTHROPIC_API_KEY"
                    if os.getenv(api_key_name):
                        available_models.append(key)
                
                if not available_models:
                    messages = self.query_one("#chat-messages")
                    error_message = Message("No API keys found. Please set either OPENAI_API_KEY or ANTHROPIC_API_KEY in your environment.", is_user=False)
                    error_message.add_class("system-message")
                    messages.mount(error_message)
                    messages.scroll_end(animate=False)
                    return 
                    
                current_index = available_models.index(self.selected_model) if self.selected_model in available_models else -1
                next_index = (current_index + 1) % len(available_models)
                self.selected_model = available_models[next_index]
                
                # update placeholder
                self._update_placeholder(input_widget)

class ChatUI(App):
    CSS_PATH = "styles/chat.css"

    def on_mount(self) -> None:
        # Check if any API keys are available
        openai_key = os.getenv("OPENAI_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        
        chat_interface = ChatInterface()
        self.push_screen(chat_interface)
        
        # If no API keys are found, show a helpful message
        if not openai_key and not anthropic_key:
            messages = chat_interface.query_one("#chat-messages")
            welcome_message = Message(
                "Welcome to the Chat App! No API keys were detected. Please set one of the following environment variables:\n"
                "- OPENAI_API_KEY for OpenAI models (gpt-4o, o1-preview, o1-mini)\n"
                "- ANTHROPIC_API_KEY for Anthropic models (claude-3-5-sonnet)\n\n"
                "You can still use the interface, but you'll need at least one valid API key to send messages.",
                is_user=False
            )
            welcome_message.add_class("system-message")
            messages.mount(welcome_message)
            messages.scroll_end(animate=False)

if __name__ == "__main__":
    ChatUI().run()