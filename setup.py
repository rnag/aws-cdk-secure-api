"""The setup script."""
import pathlib

from setuptools import setup, find_packages


here = pathlib.Path(__file__).parent

package_name = 'aws_cdk_secure_api'

packages = find_packages(include=[package_name, f'{package_name}.*'])

requires = [
    'aws-cdk-lib>=2.0.0,<3.0.0',
    'constructs>=10.0.0,<11.0.0',
    'boto3>=1.0.0,<2.0.0',
]

test_requirements = [
    'pytest~=7.0.1',
    'pytest-cov~=3.0.0',
    'pytest-runner~=5.3.1']

about = {}
exec((here / package_name / '__version__.py').read_text(), about)

readme = (here / 'README.rst').read_text()
history = (here / 'HISTORY.rst').read_text()

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/x-rst',
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    packages=packages,
    include_package_data=True,
    install_requires=requires,
    project_urls={
        'Documentation': 'https://aws-cdk-secure-api.readthedocs.io',
        'Source': 'https://github.com/rnag/aws-cdk-secure-api',
    },
    license=about['__license__'],
    # TODO add more relevant keywords as needed
    keywords=['aws-cdk', 'secure', 'rest-api', 'api-gateway', 'api key', 'cdk'],
    classifiers=[
        # Ref: https://pypi.org/classifiers/
        # 'Development Status :: 5 - Production/Stable',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python'
    ],
    test_suite='tests',
    tests_require=test_requirements,
    zip_safe=False
)
