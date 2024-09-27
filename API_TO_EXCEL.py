import pandas as pd
import logging
import os
from datetime import datetime, date, timedelta 
import json
import numpy as np

#def Setup_Logging():
BASE_PATH = r"Logging filepath"

def setup_logging(base_path):
    
    now = datetime.now()
    folder_name = now.strftime("%m%Y")
    folder_path = os.path.join(base_path, folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    log_file_name = now.strftime("%d%m.log")
    log_file_path = os.path.join(folder_path, log_file_name)
    logging.basicConfig(
        filename=log_file_path,
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    logging.debug("Logging setup complete.")

setup_logging(BASE_PATH)

class API_EXCEL:
    def Get_date_range(self):
        basepath = "Filepath for downloaded files\\Archive"
        try: 
            List_of_Files = os.listdir(basepath)
            logging.debug(List_of_Files)
            List_of_Dates = [File_name[13:23] for File_name in List_of_Files]
            logging.debug(List_of_Dates)
            List_of_Dates = [i.replace('-','') for i in List_of_Dates]
            List_of_Dates = [datetime.strptime(File_date, "%Y%m%d") for File_date in List_of_Dates]
            Latest_Date = max(dt for dt in List_of_Dates)
            Latest_Date = Latest_Date.date()
            logging.debug(List_of_Dates) 
            logging.info(Latest_Date)
        except os.listdir(basepath) == []:
            Latest_Date = date.today() - timedelta(days = 9)
        Latest_Available = date.today() - timedelta(days = 2)
        delta = Latest_Available - Latest_Date
        Files_to_Get = []
        for i in range(1,delta.days + 1):
            day = Latest_Date + timedelta(days=i)
            logging.info(day)
            Files_to_Get.append(day)
        return Files_to_Get

    def Call_API_Grab(self):
        script = "API_Expense_Grab.py"
        pythonexe = "python3"
        date1 = "--date"
        os.chdir("Local directory")
        import subprocess
        Date_Range = API_EXCEL.Get_date_range(self)
        for i in Date_Range:
            date2 = str(i)
            logging.info(date2)
            result=subprocess.run([pythonexe, script, date1, date2], capture_output=True, text=True)
            logging.info(result)

    def Match_Enfusion(self, Fees_Filtered, reference_table):
        account_list = []
        Description_row = reference_table['API Description']
        for i in Fees_Filtered['incomeSubcategoryDescription']:
            x = [i]
            Test = Description_row.isin(x)
            Test = str(Test)
            if "True" in Test:
                Account_number = reference_table[reference_table['API Description']==i]['Account Number'].item()
                account_list.append(Account_number)
                continue
            else: 
                account_list.append("NA")
                continue
        return account_list
    def Format_For_Loading(self, df_successful, i):
        df_loading = df_successful.rename(columns = {'tradeDate' : 'Date',
                                        'incomeAmountLocal' : 'CR Local Amount',
                                        'settlementCurrency' : 'CR Local CCY',
                                        'securityDescription' : 'Memo',
                                        'AccountNumber' : 'Debit Account',
                                        'Account' : 'Credit Account',
                                        'ID' : 'GL Id'})
        df_loading['DR Local Amount'] = df_loading['CR Local Amount']
        df_loading['DR Local CCY'] = df_loading['CR Local CCY']
        df_loading['Date'] = pd.to_datetime(df_loading['Date'])
        df_loading['Debit Account'] = df_loading['Debit Account'].astype(str)
        logging.info(df_loading['Date'])
        df_loading['Date'] = df_loading['Date'].dt.strftime('%m/%d/%Y') 
        logging.info(df_loading)
        df_loading = df_loading.loc[:,['GL Id', 'Date', 'Credit Account', 'Debit Account', 'CR Local Amount', 'DR Local Amount', 'CR Local CCY', 'DR Local CCY', 'Memo']]
        return df_loading

    def Write_To_Excel(self, Main_df):
        df_Expenses = []
        df_Expenses_Failed = []
        with open('Fund dictionary filepath', 'r') as f:
            data = json.load(f)
        for i in data:
            df_excel = Main_df[Main_df['accountIdCustody'] == data[i]['FUND_CODE']]
            df_excel = df_excel.assign(Destination_account = data[i]['ACCOUNT_NUMBER'], Destination_ID = data[i]['Destination_ID'])
            df_successful = df_excel.query('AccountNumber != "NA" & tradeDate == settlementDateActual')
            df_failed = df_excel.query('AccountNumber == "NA" | tradeDate != settlementDateActual')
            df_Expenses.append(API_EXCEL.Format_For_Loading(self, df_successful, i))
            df_Expenses_Failed.append(df_failed)
            continue
        df_Expenses_all = pd.concat(df_Expenses)
        df_Expenses_all.to_excel("Filepath for\\Expenses_For_Loading.xlsx", index=False)
        df_Expenses_Failed_all = pd.concat(df_Expenses_Failed)
        df_Expenses_Failed_all.to_excel("Filepath for\\Expenses_Failed.xlsx", index=False)

    def Process_Fees(self):
        base_path = "Filepath\\Fees\\"
        reference_table = pd.read_excel("Filepath\\Fees_Reference_Table.xlsx")
        logging.info(reference_table)
        List_of_dfs = []
        for i in os.listdir(base_path):
            if i == "Archive":
                continue
            else:
                Fees = pd.read_excel(base_path + i)
                Fees_Filtered = Fees[Fees["securityCategorySegmentDescription"] == "EXPENSE"]
                New_df = Fees_Filtered.assign(AccountNumber = API_EXCEL.Match_Enfusion(self, Fees_Filtered, reference_table))
                List_of_dfs.append(New_df)
        logging.info(List_of_dfs)
        if len(List_of_dfs) > 1:
            Main_df = pd.concat(List_of_dfs)
        else:
            Main_df = pd.DataFrame(List_of_dfs[0])
        Main_df['incomeAmountLocal'] = Main_df['incomeAmountLocal'].abs()
        API_EXCEL.Write_To_Excel(self, Main_df)

Test = API_EXCEL() 
Test.Call_API_Grab()   
Test.Process_Fees()




    