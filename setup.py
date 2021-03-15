"""
setup
=====

``setuptools`` for package.
"""
import setuptools

with open("README.rst") as file:
    README = file.read()


setuptools.setup(
    name="readmetester",
    version="1.0.0",
    description="Parse and test README.rst Python code-blocks",
    long_description=README,
    long_description_content_type="text/x-rst",
    author="Stephen Whitlock",
    email="stephen@jshwisolutions.com",
    maintainer="Stephen Whitlock",
    maintainer_email="stephen@jshwisolutions.com",
    url="https://github.com/jshwi/readmetester",
    copyright="2021, Stephen Whitlock",
    license="MIT",
    platforms="GNU/Linux",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    keywords=[],
    packages=setuptools.find_packages(exclude=["tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    entry_points={"console_scripts": ["readmetester=readmetester:main"]},
    python_requires=">=3.8",
)
