from setuptools import setup

setup(
    name="python-cmr",
    version="0.3.1",
    license="MIT",
    url="https://github.com/jddeal/python-cmr",
    description="Python wrapper to the NASA Common Metadata Repository (CMR) API.",
    long_description=open("README.rst").read(),
    author="Justin Deal, Matt Isnor",
    author_email="deal.justin@gmail.com, isnor.matt@gmail.com",
    packages=["cmr"],
    install_requires=[
        "requests",
    ]
)
