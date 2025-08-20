from flask import Blueprint

commands = Blueprint("commands", __name__)


@commands.cli.command()
def cli_test():
    print("GEGF")
    return ""
