from setuptools import setup, find_packages

setup(
    name="metabase-mcp",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "mcp>=1.2.0",
        "httpx>=0.24.0",
        "flask[async]>=3.1.0",
        "python-dotenv>=0.19.0",
    ],
    python_requires=">=3.8",
) 