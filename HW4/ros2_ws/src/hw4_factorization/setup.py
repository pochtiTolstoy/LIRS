from setuptools import find_packages, setup

package_name = 'hw4_factorization'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='yui',
    maintainer_email='tatolstykh@kpfu.ru',
    description='Python nodes for homework 4.',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'factor_server = hw4_factorization.factor_server:main',
            'factor_client = hw4_factorization.factor_client:main',
        ],
    },
)
