from setuptools import setup, find_packages
from version import __version__

setup(
    name='pytradingbot',
    version=__version__,
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
        "pytest-ordering",
        "pytest-cov",
        "krakenex",
        "lxml",
        "requests",
        "sphynx",
        "alive_progress",
        ]
)
        
