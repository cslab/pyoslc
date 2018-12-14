from setuptools import setup

setup(
    name='pyoslc',
    version='1.0.0',
    description='OSLC implementation to become a project in a OSLC adapter.',
    author='Koneksys LCC',
    packages=['pyoslc', 'flask.json'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'RDFLib>=4.2',
        'RDFLib-JSONLD'
    ],
)