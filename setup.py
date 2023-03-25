from setuptools import setup, find_packages

setup(
    name='pytradingbot',
    version="0.0.2",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.6",
    # description="",
    #  long_description=open('README.md').read(),
    install_requires=[
        "pandas",
        "numpy",
        "numpy_ext",
        "pytest",
        "krakenex",
        "lxml",
        "requests",
        "sphynx",
        "alive_progress",
        ]
)
        
