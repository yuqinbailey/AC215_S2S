from setuptools import find_packages
from setuptools import setup


REQUIRED_PACKAGES = ["wandb==0.15.12", "yacs", "soundfile==0.12.1", "librosa", "opencv-python","tqdm",
                     "tensorboard","chardet","charset_normalizer","future","Pillow","numba"]

# setup(
#     name="s2s-app-trainer",
#     version="0.0.1",
#     python_requires='>=3.6',
#     install_requires=REQUIRED_PACKAGES,
#     package_data={"trainer":["filelists/processed_test.txt"]},
#     packages=find_packages(),
#     description="S2S App Trainer Application"
# )

setup(
    name="s2s-app-trainer",
    version="0.0.1",
    python_requires='>=3.6',
    install_requires=REQUIRED_PACKAGES,
    packages=find_packages(),
    package_data={"":["filelists/processed_test.txt"]},
    description="S2S App Trainer Application"
)


    # packages=find_packages(where='trainer'),
    # package_dir={"": "trainer"},


