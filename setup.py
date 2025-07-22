
from setuptools import setup, find_packages
import os

# Read the contents of your README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='email-guard-sdk', 
    version='0.1.0', # Initial version
    author='Nohayla Ait Ben Salah', 
    author_email='nohaylaaitbensalh@gmail.com',
    description='A lightweight AI-powered email classification SDK for spam and phishing detection.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Nohayla10/email_guard',
    packages=find_packages(),
    package_data={
        'email_guard_sdk': ['model/email_guard_model.joblib']
    },
    include_package_data=True, 
    install_requires=[
        'scikit-learn',
        'nltk',
        'joblib',
        'numpy',
        'pandas',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Security',
        'Topic :: Text Processing',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    python_requires='>=3.9', 
)