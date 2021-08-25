from werkzeug import run_simple

from apposlc import create_oslc_app

app = create_oslc_app()

if __name__ == "__main__":
    run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)
