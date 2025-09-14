from setuptools import setup, find_packages
import os

# Read requirements
def read_requirements(file_path):
    with open(file_path) as f:
        return [
            line.strip() 
            for line in f 
            if line.strip() and not line.startswith('#') and not line.startswith('-e')
        ]

# Get long description from README
current_dir = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(current_dir, 'README.md')
long_description = ''
if os.path.exists(readme_path):
    with open(readme_path, encoding='utf-8') as f:
        long_description = f.read()

# Read requirements
requirements = read_requirements('requirements.txt')
try:
    dev_requirements = read_requirements('requirements-dev.txt')
except FileNotFoundError:
    dev_requirements = []

setup(
    name="ai_learning",
    version="0.1.0",
    description="AI Learning Platform Backend",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="BAIQ Tech",
    author_email="support@baiq-tech.com",
    url="https://github.com/baiq-tech/ai-learning",
    packages=find_packages(include=['backend', 'backend.*']),
    install_requires=requirements,
    extras_require={
        'dev': dev_requirements,
    },
    python_requires=">=3.8,<3.12",  # Ensure compatibility with Python 3.11
    include_package_data=True,
    package_data={
        'backend': ['*.py', '**/*.py', '**/*.json', '**/*.yaml', '**/*.env'],
    },
    entry_points={
        'console_scripts': [
            'ai-learning=main:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Education',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: FastAPI',
    ],
    keywords='ai education language-learning fastapi',
    project_urls={
        'Source': 'https://github.com/baiq-tech/ai-learning',
        'Bug Reports': 'https://github.com/baiq-tech/ai-learning/issues',
    },
)
