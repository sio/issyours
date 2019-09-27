from setuptools import setup, find_packages


setup(
    name='issyours',
    version='0.0.1-git',
    description='Read-only archive for any issue tracker',
    url='https://github.com/sio/issyours',
    author='Vitaly Potyarkin',
    author_email='sio.wtf@gmail.com',
    license='AGPLv3',
    platforms='any',
    entry_points={
        'console_scripts': [
            'issyours-github=issyours_github.cli:run',
        ],
    },
    packages=find_packages(exclude=('tests',)),
    include_package_data=True,
    install_requires=[
        # GitHub Fetcher
        'requests',

        # Generic Reader
        'attrs',

        # Pelican Renderer
        'pelican',
        'markdown',
    ],
    extras_require={
        'with-default-theme': [
            'alchemy @ https://github.com/nairobilug/pelican-alchemy/tarball/master',
        ],
    },
    python_requires='>=3.3',
    zip_safe=True,
)
