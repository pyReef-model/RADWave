"""
Creating PIPY package instruction:

python3 -m pip install --user --upgrade setuptools wheel
python3 setup.py sdist
python3 -m pip install --user --upgrade twine
twine check dist/*
twine upload dist/*
"""

from setuptools import setup
from os import path
import io

this_directory = path.abspath(path.dirname(__file__))
with io.open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

if __name__ == "__main__":
    setup(
        name="radwave",
        author="Tristan Salles",
        author_email="tristan.salles@sydney.edu.au",
        url="https://github.com/pyReef-model/RADWave",
        version="1.0.3",
        description="A Python interface to perform wave analysis from satellite altimeter data.",
        long_description=long_description,
        long_description_content_type="text/markdown",
        packages=["RADWave"],
        install_requires=[
            "pytest",
            "numpy>=1.15.0",
            "six>=1.11.0",
            "setuptools>=38.4.0",
            "pandas>=0.25",
            "seaborn>=0.9",
            "matplotlib>=3.0",
            "geopy>=1.20",
            "cartopy>=0.17",
            "scipy>=1.3",
            "netCDF4>=1.5.1",
            "shapely>=1.6.4",
            "scikit-image>=0.15",
            "pymannkendall>=0",
        ],
        python_requires=">=3.3",
        package_data={
            "RADWave": [
                "Notebooks/notebooks/*ipynb",
                "Notebooks/notebooks/*py",
                "Notebooks/dataset/*",
                "Notebooks/images/*",
            ]
        },
        include_package_data=True,
        classifiers=[
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
        ],
    )
