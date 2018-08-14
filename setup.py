import glob
import setuptools

setuptools.setup(
    name='start_image',
    version='0.0.1',
    description='Manages the Docker images used by START',
    author='Chris Timperley',
    author_email='christimperley@gmail.com',
    url='https://github.com/ChrisTimperley/start-image',
    install_requires=['docker'],
    include_package_data=True,
    packages=['start_image'],
    data_files=[('docker', ['Dockerfile'])],
    entry_points = {
        'console_scripts': [ 'start-cli = start_image.cli:main' ]
    }
)
