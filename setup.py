import setuptools

setuptools.setup(
    name='dao.dhcp',
    version='0.2',
    namespace_packages=['dao'],
    author='Sergii Kashaba',
    description='DAO DHCP controller',
    classifiers=[
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English'
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
    ],
    packages=setuptools.find_packages(),
    install_requires=[
        'eventlet',
        'netaddr',
        'python-daemon',
        'pyzmq',
        'sh',
        'sqlalchemy',
    ],
    tests_require=['pytest'],
    scripts=['bin/dao-dhcp', 'bin/dao-dhcp-hook'],
    entry_points={
        'console_scripts':
        ['dao-dhcp-agent = dao.dhcp.run_manager:run']},
    data_files=[('/etc/dao', ['etc/dhcp.cfg', 'etc/logger.cfg'])]
)
