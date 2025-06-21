from setuptools import setup, find_packages

with open("readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="file-transform-tools",
    version="0.1.0",
    author="mwg",
    description="Tools for transforming files using regex patterns",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mikegoelzer/file-transform-tools",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.6",
    entry_points={
        'console_scripts': [
            'replace-block=file_transform_tools.replace_block:main',
        ],
    },
    install_requires=[
        # Add any dependencies here if needed
    ],
) 