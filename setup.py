from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='pyoslc',
    version='1.0.0',
    author='Contact Software',
    author_email='fp@contact.de',
    description='SDK for implementing OSLC API using Python.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/cslab/pyoslc',
    packages=find_packages(),
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved',
        'Operating System :: OS Independent',
    ],
    keywords='OSLC, SDK, REST, API, RDF, JSON-LD',
    python_requires='>=2.7',
    install_requires=[
        'python-dotenv',
        'RDFLib>=5.0.0',
        'RDFLib-JSONLD',
        'Flask',
        'Flask-RESTx',
    ],
    extras_require={
        'dev': ['check-manifest'],
        'test': ['pytest', 'pytest-cov', 'pytest-html'],
    },
    project_urls={
        'Bug Reports': 'https://github.com/cslab/pyoslc/issues',
        'Source': 'https://github.com/cslab/pyoslc',
    },
)
