from setuptools import find_packages, setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="app",
    version="0.1",
    description="A demo application that finds the md5 hash of a file",
    packages=find_packages(where="src", include="app"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=requirements,
)
