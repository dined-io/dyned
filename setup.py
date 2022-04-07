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
            'numpy',
            'pandas',
            'scipy',
            'bokeh',
            'seaborn',
            'openpyxl',
            'requests'
      ],
      extras_require={
        'dev': [
            'pytest',
            'pytest-pep8',
            'pytest-cov',
            'jupyter',
            'notebook',
            'pylint',
            'python-dotenv'
        ]
      },
      zip_safe=False
)

