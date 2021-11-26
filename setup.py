#!/usr/bin/env python

from setuptools import setup, find_packages

python_requires='>=3, <3.9'
install_requires = ['cbpro>=1.1.4']

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='axonbot',
    version='0.2.6',
    author='Shehadi Dayekh',
    author_email='shehadi@axonintellex.com',
    license='MIT',
    url='https://github.com/axonintel/axon',
    packages=find_packages(),
    install_requires=install_requires,
    python_requires=python_requires,
    description='Axon is an artificially intelligent agent that trades bitcoin based on daily forecasts.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    download_url='https://github.com/axonintel/axon/archive/refs/heads/main.zip',
    keywords=['gdax', 'gdax-api', 'orderbook', 'trade', 'bitcoin', 'BTC', 'client', 'api', 'wrapper',
              'exchange', 'crypto', 'currency', 'trading', 'trading-api', 'coinbase', 'AI', 'ML', 'pro', 'prime', 'coinbasepro'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Information Technology',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
    ],
)
