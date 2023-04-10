from setuptools import setup
import re

version = ""

with open("ezycore/__init__.py") as f:
    contents = f.read()

    _match = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', contents, re.MULTILINE
    )

    version = _match.group(1)

if not version:
    raise RuntimeError("Cannot resolve version")

PACKAGES = [
    'ezycore',
    'ezycore.drivers',
    'ezycore.manager',
    'ezycore.models',
]
REQUIRES = ['pydantic']

setup(
    name='EzyCore',
    version=version[1:],
    description='A highly customizable cache manager for python',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    project_urls={
        'Issue Tracker': 'https://github.com/Seniatical/EzyCore/issues',
        'Homepage': 'https://github.com/Seniatical/EzyCore',
    },
    author='Seniatical',
    license='MIT License',
    packages=PACKAGES,
    install_requires=REQUIRES
)
