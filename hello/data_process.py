import numpy as np
import pandas as pd

LO_IN_ORDER = ["mcanalysis", "mcmodeling", "interpretresults", "professionalism", "pythonimplementation","caanalysis", "camodeling", "networkanalysis","networkmodeling"]
CO_IN_ORDER = ["MonteCarlo","MonteCarlo","Simulations","Simulations","Simulations","Cellular Automata","Cellular Automata","Networks","Networks"]
ASSIGNMENT_TITLES =  ["Elevator simulation",
                        "Traffic simulation",
                        "Network simulation",
                        'Final project proposal',
                        "Final project"]
ASSIGNMENT_WEIGHTS = [2, 6, 6, 0, 10]

def process_df(df):
    # replace space in header with "_"
    df.rename(columns=lambda x: x.replace(' ', '_'), inplace=True)
    # change HC column to LO and vice versa, due to error in the data
    df.rename(columns={'Learning_Outcome_Name':'HC','HC_Name':'LO' }, inplace=True)
    # removing incomplete instances with no Score data
    # data_simplified <- data_simplified[complete.cases(data_simplified$Score),]
    df.dropna(subset=['Score'], inplace=True)
    def map_CO(row, LO_IN_ORDER, CO_IN_ORDER):
        mapping = dict(zip(LO_IN_ORDER, CO_IN_ORDER)) 
    #     print(mapping)
        if not pd.isnull(row['LO']):
            return mapping[row['LO']]
        return np.nan
    df['CO'] = df.apply(lambda row: map_CO(row, LO_IN_ORDER, CO_IN_ORDER), axis=1)
    # Add weight column. Current data set does not have weights for scores. 
    def map_weight(row, ASSIGNMENT_TITLES, ASSIGNMENT_WEIGHTS):
        mapping = dict(zip(ASSIGNMENT_TITLES, ASSIGNMENT_WEIGHTS))
        if row['Assessment_Type'] != 'assignment':
            return 1
        else:
            return mapping[row['Assignment_Title']]
    df['weight'] = df.apply(lambda row: map_weight(row, ASSIGNMENT_TITLES, ASSIGNMENT_WEIGHTS), axis=1)
    # Add weighted score column                                    
    # data <- mutate(data, weighted_score = Score * weight)
    df['weighted_score'] = df['Score'] * df['weight']
    # drop null in LO column
    df.dropna(subset=['LO'], inplace=True)
    # get data only for a student (student 1 for example)
    list_of_students = df['Student_Name'].unique()
    num_students = len(list_of_students)
    i = 0
    student_name = list_of_students[i]
    student_df = df[df['Student_Name'] == student_name]
    # group by LO
    col_name_to_group_by = 'LO'
    def split_date_func(df):
        # truncate the Updated Date column so that it contains only the date information
        df['Updated_Date'] = df['Updated_Date'].str.slice(stop=10)

        # convert to DateTime
        df['Updated_Date']= pd.to_datetime(df['Updated_Date'])
    #     print(df[['Updated_Date','LO']])
        df = df.sort_values(by=['Updated_Date'])
    #     print(df[['Updated_Date','LO']])
        print('-'*10)
    #     print(df['Updated_Date'])
        # summarize the grouped Updated_Date into new columns: 'sum_weighted' and 'tot_weights'
        df = df.groupby('Updated_Date').apply(lambda x: pd.DataFrame({'sum_weighted': x['weighted_score'].sum(), 
                                                                 'tot_weights': x['weight'].sum()},
                                                                index=['Updated_Date'])).reset_index()
        df = df.drop(['level_1'], axis=1)
    #     print(df)
        ###### By this point we have a dataframe with:
          # * date
          # * total weighted scores
          # * total weights
          # What we want to do is taking the running average up to a certain date
          # For date #2, it equals: 
          # A/B where
          # A is (total weighted scores of date 1 + total weighted scores of date 2)
          # and B is (total weights of date1 + total weights of date 2)

          ## Idea: we can create 
          # * a new column (B) that is the cumsum of the vector column total weights
          # * a new column (A) that is the cumsum of the total weighted scores
          # * the quantity of interest would be A/B
        df['B'] = df['tot_weights'].cumsum(axis=0)
        df['A'] = df['sum_weighted'].cumsum(axis=0)
        df['running_avg'] = df['A'] / df['B']
#        print(df)
        return df

    data_with_avg_LO = student_df.groupby(col_name_to_group_by).apply(func=split_date_func)
    # map LO to CO
    data_with_avg_LO.reset_index(inplace=True)
    data_with_avg_LO['CO'] = data_with_avg_LO.apply(lambda row: map_CO(row, LO_IN_ORDER, CO_IN_ORDER), axis=1)
    agg = {LO: [] for LO in data_with_avg_LO['LO'].unique()}
    for index, row in data_with_avg_LO.iterrows():
        time_info = (row['Updated_Date'].year, row['Updated_Date'].month-1, row['Updated_Date'].day)
        agg[row['LO']].append(['mark',time_info, row['running_avg']])
    series = []    
    for k, v in agg.items():
        series.append({'name':k, 
                       'data': v})
    series = str(series).replace("'mark', ", "Date.UTC")
    return series

    