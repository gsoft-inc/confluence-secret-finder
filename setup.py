from setuptools import setup, find_packages

setup(
    name='confluence_secret_finder',
    version='1.0.0',
    description='Script to search Confluence Cloud for secrets.',
    url='https://github.com/gsoft-inc/confluence-secret-finder',
    author='Mathieu Gascon-Lefebvre',
    author_email='mathieuglefebvre@gmail.com',
    license='Apache',
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        'unidiff',
        'requests',
        'detect_secrets',
        'sqlitedict',
        'beautifulsoup4',
        'python-dateutil',
        'textract'
    ],
    entry_points={
        'console_scripts': ['confluence-secret-finder = confluence_secret_finder.main:main'],
    },
)