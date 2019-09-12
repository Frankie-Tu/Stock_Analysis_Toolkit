# Stock_Analysis_Toolkit

## Goal
```
A self-developed stock analysis tool aimed to ease stock valuation
process and enable user to analyze large number of stocks at scale.
```

## Mechanism
```
Perform comparative analysis on the stock symbols passed to 
Scrappers/Main.py either through input or configurations and score
each company on different categories based on how they stand against
each other to generate final scores. Stock informations are scrapped
from Yahoo Finance, thus the name Scrappers.
```

## Disclaimer
This project is based off my interests in investments and it is **only**
meant to be used as a showcase to my abilities in performing
data analysis using Pandas library and general Python programming.
Therefore, methods used to analyze stocks in this application
**do not** suggest how stocks are or should be analyzed in capital
markets by professional analysts. 


## Dependencies
```
This application was developed with Anaconda distribution (Python 3.7 version)
However, user should be able to run the application with the following dependencies:
 - Python 3
 - Requests
 - BeautifulSoup
 - Pandas
 - Numpy
 - Scipy
```

## Instructions
1.Clone repository:
- ```git clone https://github.com/Frankie-Tu/Stock_Analysis_Toolkit.git```

2.Export PYTHONPATH:
 - ```cd <project root>```
 - ```export PYTHONPATH=$(pwd)```

3.Make necessary adjustments to configurations:
- ```vi config/application_configurations.json```

4.Run application:
 - ```python3 scrapper_app.py```
