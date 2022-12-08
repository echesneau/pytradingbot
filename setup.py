from setuptools import setup, find_packages

setup(
    name='tradingbot',
    version="2.0.0",
    packages=find_packages(),
    include_package_data = True,
    python_requires=">=3.6",
    # description="",
    #  long_description=open('README.md').read(),
    install_requires=[
        "pandas",
        "numpy",
        "pytest",
        "krakenex",
        ]
)
        
