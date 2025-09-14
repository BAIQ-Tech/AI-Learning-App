from setuptools import setup, find_packages

setup(
    name="ai_learning",
    version="0.1.0",
    packages=find_packages(where="backend"),
    package_dir={"": "backend"},
    install_requires=open("backend/requirements.txt").read().splitlines(),
    python_requires=">=3.8",
)
