from setuptools import find_packages, setup

setup(
    name="ibkr-trader",
    version="0.1.0",
    description="Auto Vertical Spread Trader for Interactive Brokers",
    packages=find_packages(),
    package_dir={"": "."},
    install_requires=[
        "pandas",
        "numpy",
        "pyyaml",
        "requests",
        "python-dotenv",
        "psutil",
        "ib-insync",
        "grpcio",
        "grpcio-tools",
        "pydantic",
    ],
)

