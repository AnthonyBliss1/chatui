from dotenv import load_dotenv
from chat.ui import ChatUI
import os

if __name__ == "__main__":
    load_dotenv() 
    app = ChatUI()
    app.run()
