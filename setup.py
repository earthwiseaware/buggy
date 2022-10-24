from setuptools import setup, find_packages

setup(
    name='buggy',
    version='0.0.1',
    description='ETLs to move data from kobo to iNaturalist',
    author='Marcel Gietzmann-Sanders',
    author_email='marcelsanders96@gmail.com',
    packages=find_packages(include=['buggy', 'buggy*']),
    install_requires=[
        'httpretty',
        'pytest',
        'gluon @ git+ssh://git@github.com/networkearth/gluon'
    ]
)