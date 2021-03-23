# pylint: skip-file

from glob import glob
from os.path import basename, splitext

import setuptools

# Get the long description from the README file
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="pymessagebus",
    version="1.2.3",
    description="A simple implementation of the MessageBus / CommandBus pattern",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DrBenton/pymessagebus",
    author="Olivier Philippon",
    author_email="olivier@rougemine.com",
    license="MIT",
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords="CommandBus MessageBus CommandHandler DDD domain-driven-design design-pattern decoupling",
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob("src/**/*.py")],
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    python_requires=">=3.6",
    tests_require=[
        "pytest",
        "pylint",
        "mypy",
        "black",
    ],
)
