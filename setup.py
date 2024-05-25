from setuptools import setup, find_packages

setup(
    name='stackmap',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'wavedata',
        'python-pptx',
        'pypowerpoint',
        'wavedata',
        # 'wavedata @ git+https://github.com/decoherer/wavedata.git'
    ],
)
