from setuptools import setup, find_packages

setup(
    name="clickstream_consumer",
    version="0.1",
    packages=find_packages(exclude=['clickstream_producer']),
    install_requires=[
        # your dependencies
    ],
)