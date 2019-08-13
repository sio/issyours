from setuptools import setup, find_packages


setup(
    name='readissues',
    version='0.0.1-git',
    description='Read-only archive for any issue tracker',
    url='https://github.com/sio/readissues',
    author='Vitaly Potyarkin',
    author_email='sio.wtf@gmail.com',
    license='AGPLv3',
    platforms='any',
    entry_points={},
    packages=find_packages(exclude=('tests',)),
    include_package_data=True,
    install_requires=[
        # GitHub Fetcher
        'requests',
        'scrapehelper @ https://github.com/sio/scrapehelper/tarball/master',

        # Generic Reader
        'attrs',

        # Pelican Renderer
        'pelican',
        'markdown',
    ],
    python_requires='>=3.3',
    zip_safe=True,
)
