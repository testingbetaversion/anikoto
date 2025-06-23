from setuptools import setup, find_packages

setup(
    name='anikoto',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'requests',
        'yt-dlp',
        'bs4',

    ],
    entry_points={
        'console_scripts': [
            'anikoto=anikoto.anikoto:main',
        ],
    },
    author='testingbetaversion',
    description='Download Anime from https://anikoto.tv/',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/testingbetaversion/anikoto',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.6',
)
