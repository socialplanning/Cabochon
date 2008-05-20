#from ez_setup import use_setuptools
#use_setuptools()
from setuptools import setup, find_packages

setup(
    name='Cabochon',
    version="",
    #description="",
    author="David Turner",
    author_email="novalis@openplans.org",
    url="http://www.openplans.org/projects/cabochon",
    license="GPLv2 or any later version",
    install_requires=["Pylons>=0.9.5", "SQLObject", "restclient", "wsgiutils", "httplib2", "simplejson", "WSSEAuth", "DevAuth"],
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
    dependency_links = [
      "https://svn.openplans.org/svn/DevAuth/trunk#egg=DevAuth",
    ]
)
