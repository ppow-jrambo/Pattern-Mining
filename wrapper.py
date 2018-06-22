

"""

Wrapper class for SPMF FP-Growth Algorithm

"""


# -- imports -- #


import subprocess
import pandas as pd
from tabulate import tabulate


# -- functions -- #


def prepareData(file_location, save_location):

    # read in data

    original_data = pd.read_csv(file_location, encoding='iso-8859-2', nrows=5, delimiter='|')
    original_data = pd.read_csv(file_location, encoding='iso-8859-2', dtype=dict(zip(original_data.columns, [str] * len(original_data.columns))), delimiter='|')

    # original_data.rename(str, {'POS Txn': 'order_id', 'ID': 'item_id'}, inplace=True)

    data = original_data

    data['item'] = data['item_id'].str.strip()
    data.dropna(axis=0, subset=['order_id', 'item'], how='any', inplace=True)
    data.drop_duplicates(subset=['order_id', 'item'], inplace=True)
    data['item'] = data['item'].astype(int)
    data_consolidated = original_data[['order_id', 'item']].groupby('order_id').agg(lambda x: x.tolist())

    # save file

    if save_location[-4:] != r'.txt':
        save_location = save_location + r'.txt'

    data_consolidated['item'].to_csv(save_location, sep=' ', index=False)

    s = open(save_location).read()
    s = s.replace('"', '').replace(',', '').replace('[', '').replace(']', '')
    f = open(save_location, 'w')
    f.write(s)
    f.close()


def prepareCatalogueData(path):

    cat = pd.read_csv(path, encoding='iso-8859-2', nrows=5, delimiter='|')
    dtypes = dict(zip(cat.columns, [str] * len(cat.columns)))
    cat = pd.read_csv(path, encoding='iso-8859-2', dtype=dtypes, delimiter='|')
    cat.rename(str, {'item_id': 'PRODUCT_ID', 'item': 'NAME', 'brand': 'BRAND', 'dept': 'DEPT_NAME', 'class': 'CLASS_NAME', 'subclass': 'SUBCLASS_NAME', 'price': 'RETAIL_PRICE'}, inplace=True)
    cat_columns = ['PRODUCT_ID', 'NAME', 'BRAND', 'DEPT_NAME', 'CLASS_NAME', 'SUBCLASS_NAME', 'RETAIL_PRICE']
    cat = cat[cat_columns]
    cat.drop_duplicates(inplace=True)

    return cat


# -- classes -- #



class FPGrowth:

    def __init__(self):

        self._executable = r'./jars/spmf.jar'
        self._input = r'input.txt'
        self._output = r'output.txt'
        self._minSupp = 1


    def run(self):

        subprocess.call([r'java', r'-jar', self._executable, 'run', 'FPGrowth_itemsets', self._input, self._output, str(self._minSupp)+'%'])


    def encode_input(self, data):
        pass


    def decode_output(self):

        # read in data

        lines = []

        try:
            with open(self._output, 'rU') as f:
                lines = f.readlines()
        except:
            print('read_output error')


        # decode

        patternList = []
        supportList = []

        for line in lines:
            line = line.strip()
            delim = line.find(r'#SUP')
            patternList.append(line[0:delim].strip().split(' '))
            supportList.append(line[delim + 6:])

        patternsDict = {'Pattern': patternList, 'Support': supportList}
        patterns = pd.DataFrame(data=patternsDict, columns=['Pattern', 'Support'])

        return patterns




class FPGrowthAssociationRules:

    def __init__(self):

        self._executable = r'./jars/spmf.jar'
        self._input = r'input.txt'
        self._output = r'output.txt'
        self._minSupp = 1
        self._minConf = 1


    def run(self):

        subprocess.call([r'java', r'-jar', self._executable, 'run', 'FPGrowth_association_rules', self._input, self._output, str(self._minSupp)+'%', str(self._minConf)+'%'])


    def encode_input(self, data):
        pass


    def decode_output(self):

        # read in data

        lines = []

        try:
            with open(self._output, 'rU') as f:
                lines = f.readlines()
        except:
            print('read_output error')


        # decode

        """
        antecedentList = []
        consequentList = []
        supportList = []
        confidenceList = []
        """

        antecedentDict = {}
        consequentDict = {}
        supportDict = {}
        confidenceDict = {}

        idx = 0

        for line in lines:

            line = line.strip()

            consequenceDelim = line.find(r'==>')
            supportDelim = line.find(r'#SUP')
            confidenceDelim = line.find(r'#CONF')

            """
            antecedentList.append(line[0:consequenceDelim].strip().split(' '))
            consequentList.append(line[consequenceDelim + 4:supportDelim].strip().split(' '))
            supportList.append(line[supportDelim + 6:confidenceDelim])
            confidenceList.append(line[confidenceDelim + 7:])
            """

            antecedentDict[idx] = line[0:consequenceDelim].strip().split(' ')
            consequentDict[idx] = line[consequenceDelim + 4:supportDelim].strip().split(' ')
            supportDict[idx] = line[supportDelim + 6:confidenceDelim]
            confidenceDict[idx] = line[confidenceDelim + 7:]

            idx += 1

        """
        patternsDict = {'Antecedent': antecedentList, 'Consequent': consequentList, 'Support': supportList, 'Confidence': confidenceList}
        patterns = pd.DataFrame(data=patternsDict, columns=['Antecedent', 'Consequent', 'Support', 'Confidence'])
        """

        patterns = pd.DataFrame(data={'Dummy': list(range(idx))}, index=list(range(idx)))

        patterns['Antecedent'] = patterns['Dummy'].map(antecedentDict)
        patterns['Consequent'] = patterns['Dummy'].map(consequentDict)
        patterns['Support'] = patterns['Dummy'].map(supportDict)
        patterns['Confidence'] = patterns['Dummy'].map(confidenceDict)
        del patterns['Dummy']

        return patterns



if __name__ == '__main__':


    # prepare input data for use by FP Growth

    # prepareData(r'.\data\Product_Order_Data_06212018.csv', r'.\data\preparedFile.txt')



    """
    
    # FP Growth
    
    FP_Growth = FPGrowth()
    FP_Growth._input = r'./data/sample_data_for_FP_Growth_formatted.txt'
    FP_Growth._output = r'./outputs/output.txt'
    FP_Growth._minSupp = 0.01
    FP_Growth.encode_input([])
    FP_Growth.run()
    patternsDF = FP_Growth.decode_output()
    patternsDF = patternsDF[patternsDF['Pattern'].apply(lambda x: len(x) > 1)]
    print(tabulate(patternsDF, headers='keys', tablefmt='psql'))
    
    """


    # Association rules from FP Growth

    associationRules = FPGrowthAssociationRules()

    associationRules._input = r'./data/preparedFile.txt'
    associationRules._output = r'./outputs/output2.txt'
    associationRules._minSupp = 0.00005
    associationRules._minConf = 0.01
    associationRules.run()
    patternsDF = associationRules.decode_output()


    # get item catalogue data

    catalogue_location = r'./data/Product_Order_Data_06212018.csv'
    catalogue = prepareCatalogueData(catalogue_location)


    # prepare dictionary for mapping

    product_name_extract = catalogue[['PRODUCT_ID', 'NAME']].to_dict('split')
    product_name_dict = {i[0]: i[1] for i in product_name_extract['data']}


    # translate item IDs into names

    patternsDF['AntecedentNames'] = patternsDF.apply(lambda row: [product_name_dict[i] for i in row['Antecedent']], axis=1)
    patternsDF['ConsequentNames'] = patternsDF.apply(lambda row: [product_name_dict[i] for i in row['Consequent']], axis=1)


    # print(tabulate(patternsDF, headers='keys', tablefmt='psql'))
    patternsDF.to_excel(r'.\outputs\associations.xlsx', index=False)








# -- Graveyard --#



"""




"""