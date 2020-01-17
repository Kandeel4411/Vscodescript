#! /usr/bin/env python
import json
import re
import pathlib as pl
import sys
import subprocess
import webbrowser

import click
import pyperclip

######################################
###   Configs & Starting command   ###
######################################
BASE_DIR = pl.Path(__file__).parent
CONFIG_PATH = str(BASE_DIR / pl.Path("config.json"))


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
        try:
            with open(CONFIG_PATH) as js:
                config = json.load(js)
                ctx.obj = {
                    "project_dir": pl.Path(config["PROJECT_DIR"]),
                    "code_dir": pl.Path(config["CODE_DIR"]),
                    "clone_dir": pl.Path(config["CLONE_DIR"]),
                    "todos_app": BASE_DIR / pl.Path("todos/main.py"),
                }
        except KeyError:
            click.secho("Error: directory paths were not initialized.", fg="red")
            click.secho("Tip: consider using 'vs init' first.", fg="yellow")
            sys.exit()
        except Exception as e:
            click.secho(f"{e}", fg="red")
            sys.exit()
        else:
            for path in ctx.obj.values():
                if not path.exists():
                    click.secho("Error: invalid directory paths were given.", fg="red")
                    click.secho(
                        "Tip: consider using 'vs init' first and adding valid directory paths",
                        fg="yellow",
                    )
                    sys.exit()


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
    dirs = {
        "PROJECT_DIR": pl.Path(project_dir),
        "CODE_DIR": pl.Path(code_dir),
        "CLONE_DIR": pl.Path(clone_dir),
    }
    for d in dirs.values():
        if not d.exists():
            click.secho("Error: invalid directory paths were given.", fg="red")
            click.secho(
                "Tip: consider using 'vs init' and adding valid directory paths",
                fg="yellow",
            )
            return

    config = {}
    for dir, value in dirs.items():
        config[dir] = str(value)
    try:
        with open(CONFIG_PATH, "w") as js:
            json.dump(config, js, indent=4)
    except Exception as e:
        click.secho(f"{e}", fg="red")
        sys.exit()


######################################
###       Command:  vs code        ###
######################################
@vs.command(help=click.style("Opens given playground directory.", fg="green"))
@click.argument("dir_name")
@click.pass_context
def code(ctx, dir_name):
    click.secho("Opening...", fg="yellow")

    path = ctx.obj["code_dir"] / dir_name
    if not pl.Path.exists(path):
        pl.Path.mkdir(path)

    subprocess.Popen("code .", shell=True, cwd=path)


######################################
###     Command:  vs project       ###
######################################
@vs.command(help=click.style("Opens given project directory.", fg="green"))
@click.argument("dir_name")
@click.pass_context
def project(ctx, dir_name):
    click.secho("Opening...", fg="yellow")

    path = ctx.obj["project_dir"] / dir_name
    if not pl.Path.exists(path):
        pl.Path.mkdir(path)

    subprocess.Popen("code .", shell=True, cwd=path)




######################################
###       Command:  vs clone       ###
######################################
@vs.command(help=click.style("Clones copied github repo.", fg="green"))
@click.option("--project", is_flag=True, default=False)
@click.pass_context
def clone(ctx, project):
    click.secho("Cloning...", fg="yellow")

    clone_dir = ctx.obj["project_dir"] if project else ctx.obj["clone_dir"]
    pattern = re.compile(r"/[^/]+\.git$")
    repo = pyperclip.paste()
    try:
        path = clone_dir / pl.Path(re.search(pattern, repo).group()[1:-4])
    except AttributeError:
        click.secho("Invalid git repo.", fg="red")
        sys.exit()

    if not pl.Path.exists(path):
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
    click.secho("Starting todos...", fg="yellow")
    flask_app = subprocess.Popen(["python", str(ctx.obj["todos_app"]), CONFIG_PATH, project])
    webbrowser.open("http://localhost:5000")
    flask_app.wait()



if __name__ == "__main__":
    vs()
