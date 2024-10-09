from invoke import task


@task(aliases=["f"])
def format(c):
    """Format code."""
    c.run("black .")


@task(aliases=["c"])
def clean(c):
    """Clean up build artifacts."""
    c.run("rm -rf build dist *.egg-info")


@task(aliases=["i"])
def install(c):
    """Install dependencies."""
    c.run("pip install -r requirements.txt")


@task(aliases=["l"])
def lint(c):
    """Run linters."""
    c.run("flake8 .")


@task(aliases=["t"])
def test(c):
    """Run tests."""
    c.run("pytest")


@task(aliases=["b"])
def build(c):
    """Build the package."""
    c.run("python setup.py sdist bdist_wheel")


@task(aliases=["p"])
def publish(c):
    """Publish the package to PyPI."""
    c.run("twine upload dist/*")


@task(pre=[clean, install, lint, test, build])
def all(c):
    """Run all tasks."""
    pass