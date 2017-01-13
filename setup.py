from setuptools import setup

setup(
    name="pyCMR",
    version="0.1",
    description="Python wrapper to the NASA Common Metadata Repository API.",
    author="Justin Deal, Matt Isnor",
    author_email="deal.justin@gmail.com, isnor.matt@gmail.com",
    packages=["pyCMR"],
    install_requires=[
        "requests==2.12.4",
    ]
)
