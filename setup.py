from setuptools import setup, find_packages
from pathlib import Path

root = Path(__file__).parent.resolve()
readme_file = root / 'readme.md'
long_description = readme_file.read_text(encoding='utf-8')

setup(
    name="hubspot-api",
    version="0.6.0",
    description="Python library to interact with HubSpot's Private API",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Erol444",
    author_email="erol123444@gmail.com",
    url="https://github.com/Erol444/hubspot-api",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10"
    ],
    python_requires=">=3.6",
)
