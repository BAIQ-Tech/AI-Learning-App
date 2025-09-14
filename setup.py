from setuptools import setup, find_packages

# Read requirements
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="ai_learning",
    version="0.1.0",
    packages=find_packages(include=['backend', 'backend.*']),
    install_requires=requirements,
    python_requires=">=3.8",
    include_package_data=True,
    package_data={
        'backend': ['*.py', '**/*.py'],
    },
)
