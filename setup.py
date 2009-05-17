from setuptools import setup, find_packages
setup(
     name = "Vezilka",
     version = "0.2",
     author='Damjan Georgievski',
     author_email='gdamjan@gmail.com',
     url='http://damjan.softver.org.mk:8080/git/Vezilka.git',
     packages = find_packages(),
     install_requires=['Werkzeug', 'Genshi', 'CouchDB'],
     description = '', long_description = '',
     package_data = {},
     entry_points = {"paste.app_factory": "main=vezilka:make_app"},
)
