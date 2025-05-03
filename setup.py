from setuptools import setup, find_packages

setup(
    name="source-trace",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
        "python-dotenv>=1.0.0",
    ],
    python_requires=">=3.9",
) 