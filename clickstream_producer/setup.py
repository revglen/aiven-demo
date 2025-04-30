from setuptools import setup, find_packages

setup(
    name="clickstream_producer",
    version="0.1",
    packages=find_packages(exclude=['clickstream_consumer']),
    install_requires=[
        # your dependencies
    ],
)