from setuptools import setup, find_packages

setup(
    name='nomenklatura',
    version='3.0',
    description="Make record linkages on the web.",
    long_description='',
    classifiers=[],
    keywords='data mapping identity linkage record',
    author='Friedrich Lindenberg',
    author_email='friedrich@pudo.org',
    url='http://pudo.org',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=[],
    include_package_data=False,
    zip_safe=False,
    install_requires=[
    ],
    tests_require=[],
    entry_points={
        'nomenklatura.spiders': [
            'offshoreleaks = nomenklatura.enrichment.offshoreleaks:OffshoreLeaksSpider',
            'opencorporates = nomenklatura.enrichment.opencorp:OpenCorporatesSpider',
            'panama = nomenklatura.enrichment.panama:PanamaSpider',
            'secedgar = nomenklatura.enrichment.secedgar:SecEdgarSpider'
        ],
        'console_scripts': [
            'nk = nomenklatura.manage:main',
        ]
    },
)
