from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(
    name='Cabochon',
    version="",
    #description="",
    #author="",
    #author_email="",
    #url="",
    install_requires=["Pylons>=0.9.5", "SQLObject", "restclient", "wsgiuils"],
    packages=find_packages(),
    include_package_data=True,
    test_suite = 'nose.collector',
    package_data={'cabochon': ['i18n/*/LC_MESSAGES/*.mo']},
    entry_points="""
    [paste.app_factory]
    main=cabochon:make_app
    [paste.app_install]
    main=pylons.util:PylonsInstaller
    """,
)
