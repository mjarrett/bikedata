from distutils.core import setup

setup(name='bikedata',
      version='0.2',
      description='GBFS analytics utilities',
      author='Mike Jarrett',
      author_email='msjarrett@gmail.com',
      url='https://notes.mikejarrett.ca',
      packages=['bikedata','bikedata.weather','bikedata.plots'],
      install_requires=[
          'pandas',
          'numpy',
          'timeout_decorator',
          'geopandas',
          'cartopy',
          'seaborn',
          'glob2',
          'psutil',
          'daemoner @ https://api.github.com/repos/mjarrett/daemoner/tarball/',
          'twitterer @  https://api.github.com/repos/mjarrett/twitterer/tarball/',
      ],
     )
