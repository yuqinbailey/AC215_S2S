from setuptools import find_packages
from setuptools import setup


# REQUIRED_PACKAGES = ["wandb==0.15.12", "yacs", "soundfile==0.12.1", "librosa", "opencv-python","tqdm",
#                      "tensorboard","chardet","charset_normalizer","future","Pillow","numba"]

REQUIRED_PACKAGES = []

setup(
    name="wavenet_vocoder",
    version="0.0.1",
    python_requires='>=3.6',
    install_requires=REQUIRED_PACKAGES,
    packages=find_packages(),
    description="wavenet module"
)
