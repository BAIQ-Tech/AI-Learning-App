from setuptools import setup, find_packages
import os

# Read requirements
def read_requirements(file_path):
    requirements = []
    try:
        with open(file_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('-e'):
                    # Remove any comments at the end of the line
                    if '#' in line:
                        line = line.split('#')[0].strip()
                    if line:  # Check if there's anything left after stripping
                        requirements.append(line)
    except FileNotFoundError:
        return []
    return requirements

# Get long description from README
current_dir = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(current_dir, 'README.md')
long_description = ''
if os.path.exists(readme_path):
    with open(readme_path, encoding='utf-8') as f:
        long_description = f.read()

# Read requirements
requirements = read_requirements('requirements.txt')
dev_requirements = read_requirements('requirements-dev.txt')

# Remove any empty strings or None values
requirements = [r for r in requirements if r]
dev_requirements = [r for r in dev_requirements if r]

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
        'dev': dev_requirements
    } if dev_requirements else None,
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
