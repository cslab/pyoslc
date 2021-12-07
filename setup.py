from setuptools import setup

setup(
    name='PyOSLC',
    install_requires=[
        "python-dotenv == 0.18.0 ; python_version <= '2.7'",
        "enum34",
        "Werkzeug == 1.0.1 ; python_version <= '2.7'",
        "Werkzeug > 1.0.1 ; python_version > '2.7'",
        "click == 7.1.2 ; python_version <= '2.7'",
        "RDFLib == 5.0.0 ; python_version <= '2.7'",
        "RDFLib-JSONLD == 0.6.1 ; python_version <= '2.7'",
        "RDFLib >= 6.0.0 ; python_version > '2.7'",
        "pytest == 4.6 ; python_version <= '2.7'",
        "itsdangerous == 1.1.0 ; python_version <= '2.7'",
        "jsonschema == 3.2.0 ; python_version <= '2.7'",
        "check-manifest == 0.41 ; python_version <= '2.7'",
        "pyrsistent == 0.15.7 ; python_version <= '2.7'",
        "importlib-metadata == 2.1.1 ; python_version <= '2.7'",
        "zipp == 1.2.0 ; python_version <= '2.7'",
    ],
    extras_require={
        'dotenv': ['python-dotenv'],
        'dev': ['check-manifest'],
        'test': ['pytest', 'pytest-cov', 'pytest-html'],
    },
)
