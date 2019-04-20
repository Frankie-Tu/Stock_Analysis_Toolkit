from Scrappers.YF_Core import YF_Statement
from collections import OrderedDict
import pandas as pd
import os
import pdb

'''
designed to return the CAGR for the most important items from the three statements
'''

user_input = input("Please select the ticker you wish you analyze: ")
user_input = user_input.replace(" ", "").split(sep=",")
result_dict = OrderedDict()

n = 1

for ticker in user_input:
    statementscrap = YF_Statement.StatementScrap(ticker, storelocation="NA",
                                                 foldername="NA", filesave=False)
    print("Getting data for " + ticker)

    for statement_type in ("IS", "BS"):
        statementscrap.downloader(statement_type)
        statementscrap.growth_calculation()

        if n == 1:
            if statement_type == "IS":
                for item in [0,1,2,4,8,11,15,20,22]:
                    result_dict[statementscrap.statement_growth.index[item]] = [round(statementscrap.statement_growth.iloc[item, 3],4)]
            elif statement_type == "BS":
                for item in [5,13,17,23,32,33]:
                    result_dict[statementscrap.statement_growth.index[item]] = [round(statementscrap.statement_growth.iloc[item,3],4)]
                    n += 1
        else:
            if statement_type == "IS":
                for item in [0,1,2,4,8,11,15,20,22]:
                    result_dict[statementscrap.statement_growth.index[item]].append(round(statementscrap.statement_growth.iloc[item, 3],4))
            elif statement_type == "BS":
                for item in [5,13,17,23,32,33]:
                    result_dict[statementscrap.statement_growth.index[item]].append(round(statementscrap.statement_growth.iloc[item,3],4))

result_table = pd.DataFrame(result_dict, index=user_input).transpose()
print(result_table)

#if not os.path.exists("D:\Yahoo Finance\Stock Data\Important3"):
#    os.makedirs("D:\Yahoo Finance\Stock Data\Important3")

#result_table.to_csv("D:\Yahoo Finance\Stock Data\Important3\\file.csv")




