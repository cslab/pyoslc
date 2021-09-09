from setuptools import setup

setup(
    name='PyOSLC',
    install_requires=[
        'python-dotenv',
        'enum34',
        'Werkzeug >= 1.0',
        'click >= 7.1',
        'RDFLib>=5.0.0',
    ],
    extras_require={
        'dotenv': ['python-dotenv'],
        'dev': ['check-manifest'],
        'test': ['pytest', 'pytest-cov', 'pytest-html'],
    },
)
