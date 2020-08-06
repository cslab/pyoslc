from setuptools import setup, find_packages

setup(
    name='PyOSLC',
    version='1.0.0',
    description='OSLC implementation to become a project in a OSLC adapter.',
    author='Koneksys LCC',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'RDFLib>=5.0.0',
        'RDFLib-JSONLD',
        'Flask',
        'Flask-RESTx',
    ],
)
