#! /usr/bin/env python
import json
import re
import pathlib as pl
import sys
import subprocess
import webbrowser

import click
import pyperclip


BASE_DIR = pl.Path(__file__).parent
CONFIG_PATH = str(BASE_DIR / pl.Path("config.json"))


######################################
###        Starting command        ###
######################################
@click.group(
    help=click.style(
        "Clone/Creates project/code folder if it doesn't"
        " exist and opens it in VScode."
        "\n\nTodos app: Parses Markdown formatted .todo file from project directories"
        " and displays it on a webpage.",
        fg="yellow",
    ),
)
@click.pass_context
def vs(ctx):
    if ctx.invoked_subcommand and ctx.invoked_subcommand != "init":

        # Loading initial json configuration
        try:
            with open(CONFIG_PATH) as js:
                config = json.load(js)
                ctx.obj = {
                    "project_dir": pl.Path(config["PROJECT_DIR"]),
                    "code_dir": pl.Path(config["CODE_DIR"]),
                    "clone_dir": pl.Path(config["CLONE_DIR"]),
                    "todos_app": BASE_DIR / pl.Path("todos/main.py"),
                }

        # Wasn't able to find config file
        except FileNotFoundError:
            click.secho("Configuration file was not found.", fg="red")
            click.secho("Tip: consider using 'vs init' first to setup configuration.", fg="yellow")
            sys.exit(1)

        # Directory configuration was missing
        except KeyError:
            click.secho("Error: directory paths were not initialized.", fg="red")
            click.secho("Tip: consider using 'vs init' first.", fg="yellow")
            sys.exit(1)

        # For possible json error and other cases
        except Exception as e:
            click.secho(f"{e}.", fg="red")
            click.secho("Tip: consider using 'vs init' first as configuration may not have been initialized.", fg="yellow")
            sys.exit(1)

        # Checking if config directories actually exist
        else:
            for path in ctx.obj.values():
                if not path.exists():
                    click.secho("Error: invalid directory paths were given.", fg="red")
                    click.secho(
                        "Tip: consider using 'vs init' first and adding valid directory paths.",
                        fg="yellow",
                    )
                    sys.exit(1)


#######################################
####       Command:  vs init        ###
#######################################
@vs.command(help=click.style("Initializes directories to be used.", fg="yellow"))
@click.option(
    "--project_dir", prompt="Enter full project directory: ", type=str, required=True
)
@click.option(
    "--code_dir", prompt="Enter full code directory: ", type=str, required=True
)
@click.option(
    "--clone_dir", prompt="Enter full clone directory: ", type=str, required=True
)
def init(project_dir, code_dir, clone_dir):
    directories = {
        "PROJECT_DIR": project_dir,
        "CODE_DIR": code_dir,
        "CLONE_DIR": clone_dir,
    }

    # Creating json config file
    try:
        with open(CONFIG_PATH, "w") as js:
            json.dump(directories, js, indent=4)
    except Exception as e:
        click.secho(f"{e}", fg="red")
        sys.exit()


###########################################
###   Command:  vs code & vs project    ###
###########################################
@click.pass_context
def open_vscode(ctx, dir_name, directory):
    click.secho("Opening...", fg="yellow")

    path = ctx.obj[directory] / dir_name
    pl.Path.mkdir(path, exist_ok=True)

    subprocess.Popen("code .", shell=True, cwd=path)

#! TODO: Look for a better way to handle using the same command with different names
#! to do this without over complicating things and reptitiveness
@vs.command(help=click.style("Opens given playground directory.", fg="green"))
@click.argument("dir_name")
def code(dir_name):
    open_vscode(directory="code_dir", dir_name=dir_name)


@vs.command(help=click.style("Opens given project directory.", fg="green"))
@click.argument("dir_name")
def project(dir_name):
    open_vscode(directory="project_dir", dir_name=dir_name)



######################################
###       Command:  vs clone       ###
######################################
@vs.command(help=click.style("Clones copied github repo.", fg="green"))
@click.option("--project", is_flag=True, default=False)
@click.pass_context
def clone(ctx, project):
    click.secho("Cloning...", fg="yellow")

    # Setting directory to be cloned in projects directory if true
    clone_dir = ctx.obj["project_dir"] if project else ctx.obj["clone_dir"]

    #! TODO: Implement a better pattern for matching git repo links
    pattern = re.compile(r"/[^/]+\.git$")
    repo = pyperclip.paste()

    try:
        # Setting the directory name to be the same repo name (before the '.git')
        path = clone_dir / pl.Path(re.search(pattern, repo).group()[1:-4])

    # Valid repo pattern failed to match
    except AttributeError:
        click.secho("Invalid git repo.", fg="red")
        sys.exit()

    # Checking if it wasn't already cloned before
    if  pl.Path.exists(path):
        click.secho("Directory with the same name already exists.")
        click.secho("Opening...", fg="yellow")
    else:
        cloning = subprocess.Popen(f"git clone {repo}", cwd=clone_dir)
        cloning.wait()

    subprocess.Popen("code .", shell=True, cwd=path)


######################################
###       Command:  vs todos       ###
######################################
@vs.command(help=click.style("Opens Todos app.", fg="green"))
@click.option("-p", "--project", default="all")
@click.pass_context
def todos(ctx, project):
    click.secho("Starting Todos...", fg="yellow")
    click.secho("Press CTRL+C to exit the application.", fg="red")

    # Running todos flask application with the path to configuration and optional specific project
    flask_app = subprocess.Popen(["python", str(ctx.obj["todos_app"]), CONFIG_PATH, project])

    webbrowser.open("http://localhost:5000")
    flask_app.wait()



if __name__ == "__main__":
    vs()
