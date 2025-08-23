"""Setup file for AlphaGenome Agent package."""

from setuptools import setup, find_packages

setup(
    name="alphagenome-agent",
    version="0.1.0",
    description="TestBase Research AlphaGenome Agent",
    author="TestBase Research",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "alphagenome",
        "pydantic>=2.0",
        "requests",
        "numpy",
        "pandas",
        "matplotlib",
        "seaborn",
        "jinja2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov",
            "black",
            "isort",
            "mypy",
            "flake8",
        ]
    },
    entry_points={
        "console_scripts": [
            "alphagenome-agent=src.cli.main:main",
        ],
    },
)