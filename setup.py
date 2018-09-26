import setuptools

# Get the long description from the README file
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="pymessagebus",
    version="1.0.0",
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
        "Programming Language :: Python :: 3.6",
    ],
    keywords="CommandBus MessageBus CommandHandler",
    packages=["pymessagebus"],
    package_dir={"pymessagebus": "pymessagebus"},
    install_requires=[],
    python_requires=">=3.6",
    extras_require={"dev": [], "test": ["pytest", "pylint"]},
    setup_requires=["pytest-runner", "pytest-pylint", "pytest-mypy", "pytest-black"],
    tests_require=["pytest", "pylint", "mypy", "black"],
)
