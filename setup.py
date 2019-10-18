from setuptools import setup, find_packages

setup(name='articleHeaderPage',
      version='0.1',
      description='Creation of header page for scientific article with pdf',
      long_description="""Article Header Page creates a header page and insert
      it in front of PDF documents that contains scientific articles.""",
      classifiers=[
        'Development Status :: 0.1',
        'License :: GPL-3.0',
        'Programming Language :: Python :: 3.7',
        # 'Topic :: Image processing :: Matplotlib',
      ],
      keywords='PDF header-page article',
      python_requires='>=3.6',
      url='https://github.com/grumpfou/ArticleHeaderPage',
      author='Renaud Dessalles',
      author_email='see on my website',
      license='GPL-3.0',
      packages=find_packages(),
      # package_data = {'RFigure':['images/*.png']},
      install_requires=["pyqt5",'bibtexparser','fpdf'],
      include_package_data=True,
      # scripts=['bin/articleHeaderPage'],
      # data_files = [("config",['RFigure/RFigureConfig/RFigureHeader.py']),
                    # ("bitmaps",['RFigure/RFigureConfig/RFigureHeader.py',
                    #             ])
                    # ],
      entry_points = {
          'console_scripts': [
              'articleHeaderPage = articleHeaderPage:main',
              ]
          },
    zip_safe=False)
