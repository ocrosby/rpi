from setuptools import find_packages, setup

setup(
    name="ripper",
    version="0.1.0",
    author="Omar Crosby",
    author_email="omar.crosby@gmail.com",
    description="A CLI tool for retrieving and analyzing Soccer matches",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "requests",
        "click",
        "urllib3",
        "boto3",
        "isort",
        "pydantic",
        "numpy",
        "pandas",
        "tenacity"
        # Add other dependencies here
    ],
    extras_require={
        "dev": [
            "black",
            "isort",
            "invoke",
            "pytest",
            "pytest-cov",
            "pytest-mock",
            "coverage",
            "flake8",
            "pylint",
            "setuptools",
            "wheel",
            "twine",
            "mypy",
            "tox",
            "pre-commit",
            # Add other development dependencies here
        ]
    },
    entry_points={
        "console_scripts": [
            "ripper=ripper.cli:cli",
        ],
    },
)
