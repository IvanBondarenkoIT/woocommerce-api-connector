"""
Setup script for WooCommerce API Connector
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file, encoding="utf-8") as f:
        requirements = [
            line.strip()
            for line in f
            if line.strip() and not line.startswith("#")
        ]

setup(
    name="woocommerce-api-connector",
    version="1.0.0",
    author="Ivan Bondarenko",
    description="Python package for connecting to WooCommerce stores via REST API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/IvanBondarenkoIT/woocommerce-api-connector",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "woocommerce-connector=woocommerce_connector.connector:main",
            "woocommerce-gui=woocommerce_connector.gui:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)

