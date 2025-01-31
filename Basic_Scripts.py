import pandas as pd
import numpy as np

StandardExcel_Path = r"C:\Users\Acer\Documents\Suspension Bridge Design\Design Standards.xlsx"
Sheetname1 = "Sheet1"
TableName1 = ['Table 7.3.1']


def ExcelTable_extractor(Excel_Path, Sheetname, TableName):
    # Read the Excel file
    df = pd.read_excel(Excel_Path, sheet_name=Sheetname, engine='openpyxl')  # Load the Excel sheet as a DataFrame

    # Convert the DataFrame to a NumPy array
    array = df.values

    table_start_keywords = TableName

    # Find the indices where each table starts
    table_indices = [i for i, row in enumerate(array) if row[1] in table_start_keywords]

    #For *all type of input, provide the starting keywords of table
    TableKeywords = ["Table"]
    Captureindex_Value = ["Row", "Column"]
    if table_start_keywords[0] == "all":
        table_indices = []
        for i, row in enumerate(array):
            if isinstance(row[1], str):
                if row[1].split()[0] in TableKeywords:
                    table_indices.append(i)

    table_indices.append(len(array))
    # Split the array into tables and clean empty columns
    tables = []
    for i in range(len(table_indices) - 1):
        start_idx = table_indices[i] # Skip headers
        end_idx = table_indices[i + 1]
        tables.append(array[start_idx:end_idx])


    #Processing for tables


    #Skipping the headers based on row and column as provided
    Setback_RowColumn = []          #It captures the values to be set back for each row from table indexed row and column from 0. ie the position of core table
    #1 Identifying if the skipping values are provided or not
    for table in tables:
        checkRowCol = False
        for data in table:
            checkRowCol = set(Captureindex_Value).issubset(set(data))

            if checkRowCol:
                Col_Row = []
                for value in data:
                    if isinstance(value, int):
                        Col_Row.append(value)
                Setback_RowColumn.append(Col_Row[:2])
                break

        if not checkRowCol:
            Setback_RowColumn.append([1,1])

    def trailingtable_splitting(tables):
        #Removing for the trailing tables except the one desirec (first one)(As tables starts from Name specified table till the end)
        TrailingTable_index = None
        count = 0
        for i, row in enumerate(tables):
            for keyword in TableKeywords:
                if keyword in str(row[0]):
                    count += 1
                    if count == 2:
                        TrailingTable_index = i
                        break
        if not TrailingTable_index == None:
            return tables[:TrailingTable_index]
        else:
            return tables

    #2 Now clipping the tables based on the provided information in #1
    dyn_tables = []
    for index, table in enumerate(tables):
        # 3 Removing all teh nan values from the table
        tabledata = table[:, Setback_RowColumn[index][0]:]   #Column slicing
        tabledata = trailingtable_splitting(tabledata)          #Extracting the desired table only by removing other trailing, Table string must be in first (o index) before calling the function

        tabledata = tabledata[Setback_RowColumn[index][1]:]          #Row slicing based on excel provided values

        tabledata = tabledata[:, ~np.all(pd.isna(tabledata), axis=0)]   #Column removal with all value as nan
        tabledata = tabledata[~np.all(pd.isna(tabledata), axis=1)]      #Rows removal with all value as nan




        dyn_tables.append(tabledata)
    tables = dyn_tables





    # ### Display the tables
    # for idx, table in enumerate(tables, start=1):
    #     print(f"Table {idx}:\n", table)
    #     print("\n")

    return tables

def Table_Scraping(Table, SearchHeading, SearchValue, TargetHeading, SearchValueMultiplier = 1, JustGreater=False, wholeRow = False):
    Header = Table[0]
    TableValues = Table[1:]

    SearchHeading_Index = next((i for i, value in enumerate(Header) if str(SearchHeading).lower() in value.lower()), None)
    TargetHeading_Index = next((i for i, value in enumerate(Header) if str(TargetHeading).lower() in value.lower()), None)

    # TargetRow = next((i for i, value in enumerate(TableValues) if DiaHeader.lower() in value.lower()), None)
    TargetRow = 0
    for index, value in enumerate(TableValues):
        SearchRef = value[SearchHeading_Index]
        if (isinstance(SearchRef, str) and isinstance(SearchValue, str)) or (isinstance(SearchRef, str) and (isinstance(SearchValue, int) or isinstance(SearchValue, float))):
            if SearchValue.lower() in str(SearchRef).lower():
                TargetRow = index
                if JustGreater:
                    try:
                        Check = value[index + 1]
                        TargetRow = index + 1
                    except:
                        TargetRow = index
                break

        if not (isinstance(SearchRef, str) and isinstance(SearchValue, str)):
            ExactSearchRef = SearchRef * SearchValueMultiplier
            if JustGreater:
                if float(ExactSearchRef) > float(SearchValue):
                    TargetRow = index
                    break

            else:
                if float(ExactSearchRef) == float(SearchValue):
                    TargetRow = index
                    break

                elif float(ExactSearchRef) > float(SearchValue):
                    TargetRow = index
                    break

    TargetValue = TableValues[TargetRow][TargetHeading_Index]

    if wholeRow:
        result_row = TableValues[TargetRow]
        TitleValues_Dict = dict((zip(Header, result_row)))
        return TitleValues_Dict

    return TargetValue


# Table_List = ExcelTable_extractor(
#     Excel_Path=r"C:\Users\Acer\Documents\Suspension Bridge Design\Design Standards.xlsx", Sheetname="Sheet1",
#     TableName=['Table 7.3.1'])
# print(", final output", Table_List)


def dictValuefromTitlekey(dictionary, partial_key):
    for key in dictionary:
        if partial_key in key:
            return dictionary[key]
    return None  # Return None if no key contains the partial string