from setuptools import setup, find_packages

setup(
    name="email_guard",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "flask==2.3.2",
        "flask-limiter==2.8.1",
        "transformers==4.30.0",
        "torch==2.7.1",
        "gunicorn==20.1.0"
    ],
    python_requires=">=3.8",
)