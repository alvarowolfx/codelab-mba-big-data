import setuptools

# NOTE: Any additional file besides the `main.py` file has to be in a module
#       (inside a directory) so it can be packaged and staged correctly for
#       cloud runs.

REQUIRED_PACKAGES = [
    'apache-beam[gcp]',
    'Keras==2.2.4',
    'tensorflow==1.11.0',
    'numpy==1.16.2',
    'Pillow==5.4.1',
    'requests==2.21.0',
]

setuptools.setup(
    name='mba-senai',
    version='0.0.1',
    install_requires=REQUIRED_PACKAGES,
    packages=setuptools.find_packages(),
    include_package_data=True,
    description='Cloud ML molecules sample with preprocessing',
)
