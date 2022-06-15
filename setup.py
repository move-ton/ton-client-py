import setuptools


with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ton-client-py",
    version="1.34.2.0",
    author="MoveTON",
    author_email="",
    description="Python SDK for Everscale",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/move-ton/ton-client-py",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[],
)
