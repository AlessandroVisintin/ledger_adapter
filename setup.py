from setuptools import setup, find_packages

setup(
    name='LedgerAdapter',
    version='2.0',
    packages=find_packages(),
    install_requires=[
        "cryptography==46.0.3",
        "eth-abi==5.2.0",
        "eth-account==0.13.7",
        "hexbytes==1.3.1",
        "PyJWT==2.10.1",
        "requests==2.32.5",
        "web3==7.14.0",
        "pytest==9.0.2",
        "pytest-mock==3.15.1",
        "python-dotenv==1.2.1"
    ]
)