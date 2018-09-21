"""
Command line interface for deeptracy.

"""
from deeptracy import Config
from deeptracy import model
from deeptracy.web import application


def main():
    """Initialize and start the application."""
    model.init()

    print("Starting application")
    application.run(host=Config.HOST,
                    port=Config.PORT,
                    reloader=Config.DEBUG)
