from deeptracy import Config
from deeptracy import model
from deeptracy.web import application

import time


def main():
    model.init()

    print("Starting application")
    application.run(host=Config.HOST,
                    port=Config.PORT,
                    reloader=Config.DEBUG)
