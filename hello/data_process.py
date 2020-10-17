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
DEFAULT_LO_TO_DISPLAY_IN_EVOLUTION = ['networkanalysis', 'networkmodeling']

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
    lo_evolution_data = []
    intermediate_whole_class_lo_data = {LO: [] for LO in df['LO'].unique()}
    # data for plotting LO averages
    LO_avg_data = []

    def match_color(val):
        # SET COLOR TO MATCH MINERVA SCHEME
        if 0 < val and val < 2:
            color = '#C83F31'
        elif 2 <= val and val < 3:
            color = '#DB883A'
        elif 3 <= val and val < 4:
            color = '#56A371'
        elif 4 <= val and val < 5:
            color = '#3473B6'
        elif 5 <= val:
            color = '#573F88'
        return color
    def split_date_func(df):
        # truncate the Updated Date column so that it contains only the date information
        df['Updated_Date'] = df['Updated_Date'].str.slice(stop=10)

        # convert to DateTime
        df['Updated_Date']= pd.to_datetime(df['Updated_Date'])
    #     print(df[['Updated_Date','LO']])
        df = df.sort_values(by=['Updated_Date'])
    #     print(df[['Updated_Date','LO']])
    #         print('-'*10)
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
        df['cumsum_tot_weights'] = df['tot_weights'].cumsum(axis=0)
        df['cumsum_sum_weighted'] = df['sum_weighted'].cumsum(axis=0)
        df['running_avg'] = df['cumsum_sum_weighted'] / df['cumsum_tot_weights']
    #        print(df)
        return df


    for i in range(num_students):
        student_name = list_of_students[i]
        student_df = df[df['Student_Name'] == student_name]
        # group by LO
        col_name_to_group_by = 'LO'

        data_with_avg_LO = student_df.groupby(col_name_to_group_by).apply(func=split_date_func)
        # map LO to CO
        data_with_avg_LO.reset_index(inplace=True)
        data_with_avg_LO['CO'] = data_with_avg_LO.apply(lambda row: map_CO(row, LO_IN_ORDER, CO_IN_ORDER), axis=1)
        agg = {LO: {'visible': False, 'content': []} for LO in data_with_avg_LO['LO'].unique()}
        for index, row in data_with_avg_LO.iterrows():
            time_info = (row['Updated_Date'].year, row['Updated_Date'].month-1, row['Updated_Date'].day)
            if row['LO'] in DEFAULT_LO_TO_DISPLAY_IN_EVOLUTION:
                visible = True
            else:
                visible = False
            agg[row['LO']]['visible'] = visible
            agg[row['LO']]['content'].append(['mark',time_info, row['running_avg']])

        series = []    
        for k, v in agg.items():
            series.append({'name':k, 
                           'data': v['content'],
                           'visible': v['visible']})
            intermediate_whole_class_lo_data[k].append(v['content'][-1][-1])
        LO_avg_this_student = {}
        LO_avg_this_student['student_name'] = student_name
        LO_avg_this_student['LO'] = []
        LO_avg_this_student['LO_avg'] = []
        LO_avg_this_student['color'] = []
        for LO in series:
            LO_avg_this_student['LO'].append(LO['name'])

            # SET COLOR TO MATCH MINERVA SCHEME
            color = match_color(LO['data'][-1][-1])
            LO_avg_this_student['LO_avg'].append({'y': LO['data'][-1][-1],
                                                  'color': color})
    #         LO_avg_this_student['color'].append(color)


        LO_avg_data.append(LO_avg_this_student)

        series = str(series).replace("'mark', ", "Date.UTC")
        series = series.replace("True", 'true')
        series = series.replace("False", 'false')
        # add this student's data to data for plotting LO evolution
        lo_evolution_data.append({'student_name': student_name, 'series': series})
    # print(lo_evolution_data)
    # compute summary stats for LO averages for the whole class
    whole_class_lo_data = {'LO': [], 'mean': [], 'range':[]} 
    # print(len(intermediate_whole_class_lo_data['pythonimplementation']))
    for k, v in intermediate_whole_class_lo_data.items():
        whole_class_lo_data['LO'].append(k)
        # compute mean
        mean = np.mean(v)
        whole_class_lo_data['mean'].append(mean)
        # compute range
        min_val = np.min(v)
        max_val = np.max(v)
        whole_class_lo_data['range'].append([min_val, max_val])

    
    CO_avg_data = []
    for i in range(num_students):
        student_name = list_of_students[i]
        student_df = df[df['Student_Name'] == student_name]
        # group by CO
        col_name_to_group_by = 'CO'

        data_CO_evolution = student_df.groupby(col_name_to_group_by).apply(func=split_date_func)
        data_CO_avg = data_CO_evolution.groupby(col_name_to_group_by).tail(1)
        data_CO_avg.reset_index(inplace=True)
    #     data_with_avg_CO.reset_index(inplace=True)
    #     data_with_avg_LO['CO'] = data_with_avg_LO.apply(lambda row: map_CO(row, LO_IN_ORDER, CO_IN_ORDER), axis=1)
    # data_with_avg_CO.head()

        CO_avg_this_student = {}
        CO_avg_this_student['student_name'] = student_name
        CO_avg_this_student['CO'] = []
        CO_avg_this_student['CO_avg'] = []
        CO_avg_this_student['color'] = []
        CO_avg_this_student['course_avg'] = [np.mean(data_CO_avg['running_avg'])]*data_CO_avg.shape[0]
        for index, row in data_CO_avg.iterrows():
            CO_avg_this_student['CO'].append(row['CO'])
            # SET COLOR TO MATCH MINERVA SCHEME
            color = match_color(row['running_avg'])
            CO_avg_this_student['CO_avg'].append({'y': row['running_avg'],
                                                  'color': color})
        CO_avg_data.append(CO_avg_this_student)
    
    # LO contribution
    intermediate_data_whole_class_LO_contrib = {LO: [] for LO in df['LO'].unique()}
    LO_contrib_data = []
    # print(intermediate_data_whole_class_LO_contrib)
    for i in range(num_students):
        student_name = list_of_students[i]
        student_df = df[df['Student_Name'] == student_name]
        # group by CO
        col_name_to_group_by = 'CO'
        data_with_avg_CO = student_df.groupby(col_name_to_group_by).apply(func=split_date_func)
        data_with_avg_CO = data_with_avg_CO.groupby(col_name_to_group_by).tail(1)
        data_with_avg_CO.reset_index(inplace=True)
        num_CO = data_with_avg_CO.shape[0]

        # group by LO
        col_name_to_group_by = 'LO'
        data_with_avg_LO = student_df.groupby(col_name_to_group_by).apply(func=split_date_func)
        data_with_avg_LO = data_with_avg_LO.groupby(col_name_to_group_by).tail(1)
        data_with_avg_LO.reset_index(inplace=True)
        # map LO to CO
        data_with_avg_LO['CO'] = data_with_avg_LO.apply(lambda row: map_CO(row, LO_IN_ORDER, CO_IN_ORDER), axis=1)

        # lookup CO table from LO table
        data_with_avg_LO = data_with_avg_LO.merge(data_with_avg_CO, on="CO")
        data_with_avg_LO['LO_contrib'] = data_with_avg_LO['cumsum_sum_weighted_x']/data_with_avg_LO['cumsum_tot_weights_y']/num_CO/np.mean(data_with_avg_CO['running_avg'])
        for k,v in data_with_avg_LO.iterrows():
            intermediate_data_whole_class_LO_contrib[v['LO']].append(v['LO_contrib'])

        LO_contrib_data_this_student = {}
        LO_contrib_data_this_student['LO'] = list(data_with_avg_LO['LO'])
        LO_contrib_data_this_student['LO_avg'] = list(data_with_avg_LO['LO_contrib'])
        LO_contrib_data_this_student['student_name'] = student_name
        LO_contrib_data.append(LO_contrib_data_this_student)

    # compute summary stats for LO averages for the whole class
    whole_class_lo_contrib_data = {'LO': [], 'mean': [], 'range':[]} 
    for k, v in intermediate_data_whole_class_LO_contrib.items():
        whole_class_lo_contrib_data['LO'].append(k)
        # compute mean
        mean = np.mean(v)
        whole_class_lo_contrib_data['mean'].append(mean)
        # compute range
        min_val = np.min(v)
        max_val = np.max(v)
        whole_class_lo_contrib_data['range'].append([min_val, max_val])

    return lo_evolution_data, whole_class_lo_data, LO_avg_data, CO_avg_data, whole_class_lo_contrib_data, LO_contrib_data

    