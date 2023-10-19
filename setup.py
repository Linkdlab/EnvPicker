from setuptools import setup, find_packages
import envpicker

from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="envpicker",
    version=envpicker.__version__,
    description="automatic picking of environments",
    long_description=long_description,
    author="Julian Kimmig",
    author_email="julian.kimmig@linkdlab.de",
    packages=find_packages(),  # Update with your package name
    install_requires=["pyyaml"],
    # github
    url="https://github.com/Linkdlab/EnvPicker",
    # license
    license="MIT",
    long_description_content_type="text/markdown",
    # classifiers
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",  # Adjust to your Python version
    ],
)
