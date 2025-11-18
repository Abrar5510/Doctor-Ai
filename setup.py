"""
Setup configuration for Doctor-AI
This ensures setuptools>=70.0.0 is available before building dependencies
"""

from setuptools import setup, find_packages

# Minimal setup.py to ensure proper setuptools version
# The main dependencies are in requirements.txt

setup(
    name="doctor-ai",
    version="0.1.0",
    description="Medical Symptom Constellation Mapper - AI-powered diagnostic support system",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    setup_requires=[
        "setuptools>=70.0.0",
    ],
    install_requires=[
        # Dependencies are managed via requirements.txt
        # This minimal list ensures build compatibility
        "setuptools>=70.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "black",
            "isort",
            "flake8",
        ],
    },
)
