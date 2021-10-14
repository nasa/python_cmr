from setuptools import setup

setup(
    name="python-cmr",
    version="0.4.1",
    license="MIT",
    url="https://github.com/nasa/python_cmr",
    description="Python wrapper to the NASA Common Metadata Repository (CMR) API.",
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    author="https://github.com/orgs/nasa/teams/python-cmr",
    packages=["cmr"],
    install_requires=[
        "requests",
    ]
)
