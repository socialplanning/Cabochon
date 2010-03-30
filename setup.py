#from ez_setup import use_setuptools
#use_setuptools()
from setuptools import setup, find_packages

setup(
    name='Cabochon',
    version="0.2",
    #description="",
    author="David Turner",
    author_email="novalis@openplans.org",
    url="http://www.openplans.org/projects/cabochon",
    license="GPLv2 or any later version",
    install_requires=[
        "Routes==1.11",
        "Pylons==0.9.6.2",
        "SQLObject", 
        "restclient", 
        "WSGIUtils",
        "httplib2",
        "simplejson", 
        "WSSEAuth",
        "DevAuth",
        "SupervisorErrorMiddleware"
        ],
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
      "https://svn.openplans.org/svn/SupervisorErrorMiddleware/trunk#egg=SupervisorErrorMiddleware-dev",
    ]
)
