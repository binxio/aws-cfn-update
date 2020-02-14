"""
Programmatically update CloudFormation templates
"""
from setuptools import find_packages, setup

dependencies = ['click', 'boto3', 'cfn-flip', 'pytz', 'pytest', 'croniter', 'tzlocal', 'click-datetime', 'ruamel.yaml==0.16.5', 'jsonmerge']

setup(
    name='aws-cfn-update',
    version="0.3.6",
    url='https://github.com/mvanholsteijn/aws-cfn-update',
    license='BSD',
    author='Mark van Holsteijn',
    author_email='mark@binx.io',
    description='Programmatically update CloudFormation templates',
    long_description=__doc__,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=dependencies,
    setup_requires=['pytest-runner'],
    tests_require=dependencies + ['pytest'],
    test_suite='tests',
    entry_points={
        'console_scripts': [
            'aws-cfn-update = aws_cfn_update.cli:main',
        ],
    },
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
