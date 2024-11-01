from setuptools import setup, find_packages

with open("README.md", "r", encoding="UTF-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="UTF-8") as f:
    requirements = [line.strip() for line in f]

setup(
    name='nameapi-client-python',
    version='1.0.1',
    description='Python Client for the NameAPI Web Services',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.nameapi.org/",
    project_urls={
        'Source Code': 'https://github.com/optimaize/nameapi-client-python',
        'Bug Tracker': 'https://github.com/optimaize/nameapi-client-python/issues',
    },
    packages=find_packages(),
    keywords=['nameapi', 'rest nameapi', 'nameapi client', 'name parser', 'name matcher', 'person risk detector',
              'name genderizer', 'email name parser', 'email parser', 'disposable email detector', 'dea detector'],
    test_suite='tests/tests.py',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    install_requires=requirements,
)
