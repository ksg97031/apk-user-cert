import sys
import setuptools

if sys.version_info < (3, 5, 3):
    print("Unfortunately, your python version is not supported!\n"
          + "Please upgrade at least to Python 3.5.3!")
    sys.exit(1)

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="apk-user-cert",
    python_requires='>=3.5.3',
    version="1.0.3",
    author="ksg97031",
    author_email="ksg97031@gmail.com",
    description="Set network_security_config.xml and android:networkSecurityConfig",
    install_requires=['click'],
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/ksg97031/apk-user-cert",
    packages=setuptools.find_packages(),
    package_data={'scripts':
             ["files/network_security_config.xml"]},
    entry_points={
        'console_scripts': [
            'apk-user-cert = scripts.cli:run'
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
