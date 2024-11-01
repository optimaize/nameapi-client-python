from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as f:
    requirements = [line.strip() for line in f]

setup(
    name='nameapi-client-python',
    version='1.0.0',
    description='Python Client for the NameAPI Web Service ',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/optimaize/nameapi-client-python",
    packages=find_packages(),
    keywords=['nameapi', 'rest nameapi', 'nameapi client', 'python nameapi', 'nameapi python client'],
    test_suite='tests/tests.py',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    install_requires=requirements,
)
