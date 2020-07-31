from setuptools import setup, find_packages

setup(
    name='PyOSLC-API ',
    version='1.0.0',
    description='PyOSLC REST API Example.',
    author='Koneksys LCC',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask',
        'Flas-RESTPlus',
        'RDFLib>=5.0',
        'RDFLib-JSONLD'
    ],
)
