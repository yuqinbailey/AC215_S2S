from setuptools import find_packages
from setuptools import setup


REQUIRED_PACKAGES = ["wandb==0.15.12", "yacs", "soundfile==0.12.1"]

setup(
    name="s2s-app-trainer",
    version="0.0.1",
    install_requires=REQUIRED_PACKAGES,
    packages=find_packages(),
    description="S2S App Trainer Application",
)
