from setuptools import setup

setup(
    name="pycmr",
    version="0.1",
    description="Python wrapper to the NASA Common Metadata Repository API.",
    author="Justin Deal, Matt Isnor",
    author_email="deal.justin@gmail.com, isnor.matt@gmail.com",
    packages=["pycmr"],
    install_requires=[
        "requests==2.12.4",
    ]
)
