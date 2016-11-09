from setuptools import setup, find_packages

setup(
    name = "swamp-python-api",
    version = "0.1",
    packages = find_packages('src'),
    package_dir = {'':'src'},
    install_requires = ['requests'],
    entry_points = {
        'console_scripts': [
            'swamp-api = swamp_api.__main__:main',
        ],
    },
    include_package_data = True,

    # metadata for upload to PyPI
    author = "Vamshi Basupalli",
    author_email = "vamshi@cs.wisc.edu",
    description = "Swamp Python API",
    license = "MIT",
)

