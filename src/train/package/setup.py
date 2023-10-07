from setuptools import find_packages
from setuptools import setup


REQUIRED_PACKAGES = ["wandb==0.15.12", "yacs", "soundfile==0.12.1", "librosa", "opencv-python","tqdm",
                     "tensorboard","chardet","charset_normalizer","future","Pillow","numba"]

setup(
    name="s2s",
    version="0.0.1",
    python_requires='>=3.6',
    install_requires=REQUIRED_PACKAGES,
    packages=find_packages(),
    package_data={"":["filelists/processed_test.txt"]},
    description="S2S App Trainer Application"
)
