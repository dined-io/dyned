from setuptools import setup, find_packages

setup(name='dined',
      version='0.1',
      description='Dined - Anthropometry in Design',
      url='http://github.com/dined-io/dyned',
      author='Delft University of Technology',
      author_email='dined-io@tudelft.nl',
      license='BSD',
      packages=find_packages(),
      install_requires=[
            'numpy==1.22.3',
            'pandas==1.4.2',
            'scipy==1.8.0',
            'bokeh==2.4.2',
            'seaborn==0.11.2',
            'openpyxl==3.0.9',
            'requests==2.27.1'
      ],
      extras_require={
        'dev': [
            'pytest==7.1.1',
            'pytest-pep8==1.0.6',
            'pytest-cov==3.0.0',
            'jupyter==1.0.0',
            'notebook==6.4.10',
            'pylint==2.13.5',
            'python-dotenv==0.20.0',
            'mysql-connector-python==8.0.28', #TODO: Remove later this is necessesary for exporting the current database to csvs
            'SQLAlchemy==1.4.35'
        ]
      },
      zip_safe=False
)

