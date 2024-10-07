from invoke import task


@task(name="f")
def forma_codet(c):
    """Format code using black."""
    c.run("isort .")
    c.run("black .")


@task(name="t")
def test(c):
    """Run tests."""
    c.run("pytest")


@task(name="l")
def lint(c):
    """Lint code using flake8."""
    c.run("flake8 ripper setup.py tasks.py")
    c.run("pylint ripper setup.py tasks.py")


@task(name="r")
def run(c):
    """Run the application."""
    c.run("python main.py")


@task(name="i")
def install(c):
    """Install required packages."""
    c.run("echo 'Upgrading pip ...'")
    c.run("pip install --upgrade pip")

    c.run("echo 'Installing dependencies ...'")
    c.run("pip install '.[dev]'")

    c.run("echo 'Installing the pre-commit hooks ...'")
    c.run("pre-commit install")


@task(name="h")
def hooks(c):
    """Run the pre-commit hooks manually on all files."""
    c.run("pre-commit run --all-files")
