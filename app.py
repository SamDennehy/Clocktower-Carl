import threading

from bot import run_bot
from web_app import run_web_server


def main():
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()
    run_bot()


if __name__ == "__main__":
    main()
