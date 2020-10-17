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
    def set_color(row, col_name):
        return match_color(row[col_name])

    def split_date_func(df):
        # truncate the Updated Date column so that it contains only the date information
        df['Updated_Date'] = df['Updated_Date'].str.slice(stop=10)

        # convert to DateTime
        df['Updated_Date']= pd.to_datetime(df['Updated_Date'])
        df = df.sort_values(by=['Updated_Date'])
        # summarize the grouped Updated_Date into new columns: 'sum_weighted' and 'tot_weights'
        df = df.groupby('Updated_Date').apply(lambda x: pd.DataFrame({'sum_weighted': x['weighted_score'].sum(), 
                                                                 'tot_weights': x['weight'].sum()},
                                                                index=['Updated_Date'])).reset_index()
        df = df.drop(['level_1'], axis=1)
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
        return df

    def group_by_student(col_name_to_group_by, evolution=True):
        """
        return a list of df, each df corresponds to a student.
        - col_name_to_group_by: 'LO' or 'CO'
        """
        df_list = []

        for i in range(num_students):
            student_name = list_of_students[i]
            student_df = df[df['Student_Name'] == student_name]
            # group by LO or CO
            data_with_avg = student_df.groupby(col_name_to_group_by).apply(func=split_date_func)
            if not evolution: # obtain only the latest average score
                data_with_avg = data_with_avg.groupby(col_name_to_group_by).tail(1)
            data_with_avg.reset_index(inplace=True)

            # map LO to CO
            if col_name_to_group_by == 'LO':
                data_with_avg['CO'] = data_with_avg.apply(lambda row: map_CO(row, LO_IN_ORDER, CO_IN_ORDER), axis=1)
            # set color
            data_with_avg['color'] = data_with_avg.apply (lambda row: set_color(row, 'running_avg'), axis=1)
            df_list.append(data_with_avg)

        return df_list

    # LO Evolution
    LO_evolution_list = group_by_student('LO')
    LO_evolution_data = []
    for i, student_df in enumerate(LO_evolution_list):
        out = {'student_name': list_of_students[i]}
        out['series'] = []
        """
        out['series'] is of str type
        out['series'] = [{'name': 'caanalysis', 
                          'data': [[Date.UTC(2020, 0, 28), 4.0], [Date.UTC(2020, 1, 3), 3.5]], 
                          'visible': False},
                          {...}]
        """
        for LO, group_df in student_df.groupby('LO'):
            series_info = {'name': LO, 
                           'visible': LO in DEFAULT_LO_TO_DISPLAY_IN_EVOLUTION}
            series_info['data'] = []
            for index, row in group_df.iterrows():
                datetime = row['Updated_Date']
                series_info['data'].append(['Date.UTC',(datetime.year, datetime.month-1, datetime.day), row['running_avg']])
            out['series'].append(series_info)
        out['series'] = str(out['series']).replace("'Date.UTC', ", "Date.UTC").replace("False", "false").replace("True", "true")
        LO_evolution_data.append(out)

    # LO average
    def get_average_data(category_col, average_list, data_col='running_avg', color_col='color'):
    #     average_list = group_by_student(col_name_to_group_by, evolution=False)
        average_data = []
        for i, student_df in enumerate(average_list):
            out = {'student_name': list_of_students[i],
                    'categories': list(student_df[category_col]),
                   'mean_of_avg': [np.mean(student_df[data_col])]*student_df.shape[0]}
            """
            out['avg'] = [{'y': 3.5, 'color': '#56A371'},
                          {...},
                          ...]
            """
            out['data'] = []
            for index, row in student_df.iterrows():
                if color_col is None:
                    color = 'black'
                else:
                    color = row[color_col]

                out['data'].append({'y': row[data_col],
                                   'color': color})
            average_data.append(out)
        return average_data
    LO_average_df_list = group_by_student(col_name_to_group_by='LO', evolution=False)
    LO_average_data = get_average_data('LO', LO_average_df_list)
    # LO mean and range for whole class 
    def get_summary_stat_data(df_list, val_col):
        summary_stat_data = {'LO': [LO for LO in df['LO'].unique()],
                             'mean': [],
                             'range': []}
        for i, student_df in enumerate(df_list):
            student_df = student_df[['LO', val_col]]
            if i == 0:
                merged_df = student_df
            else:
                merged_df = merged_df.merge(student_df, on='LO')
        merged_df['mean'] = merged_df.loc[:, merged_df.columns != 'LO'].mean(axis=1)
        merged_df['min'] = merged_df.loc[:, merged_df.columns != 'LO'].min(axis=1)
        merged_df['max'] = merged_df.loc[:, merged_df.columns != 'LO'].max(axis=1)
        merged_df['range'] = merged_df.apply(lambda x: [x['min'], x['max']], axis=1)
        summary_stat_data = {'LO': list(merged_df['LO']),
                             'mean': list(merged_df['mean']),
                             'range': list(merged_df['range'])}
        return summary_stat_data
    LO_summary_stat_data = get_summary_stat_data(df_list=LO_average_df_list,
                                                 val_col='running_avg')

    # CO average
    CO_average_df_list = group_by_student(col_name_to_group_by='CO', evolution=False)
    CO_average_data = get_average_data('CO', CO_average_df_list)


    # LO contribution
    ## for indvidual student 
    contrib_df_list = []
    for i, m in enumerate(zip(LO_average_df_list, CO_average_df_list)):
        # lookup CO table from LO table
        LO_df, CO_df = m
        num_CO = CO_df.shape[0]
        contrib_df = LO_df.merge(CO_df, on="CO")
        contrib_df['LO_contrib'] = contrib_df['cumsum_sum_weighted_x']/contrib_df['cumsum_tot_weights_y']/num_CO/np.mean(CO_df['running_avg'])
        contrib_df = contrib_df[['LO', 'LO_contrib']]
        contrib_df_list.append(contrib_df)
    # print(contrib_df_list[0])
    LO_contrib_data = get_average_data('LO', contrib_df_list, data_col='LO_contrib', color_col=None)


    ## summary stats for whole class
    contrib_summary_stat_data = get_summary_stat_data(df_list=contrib_df_list,
                                                 val_col='LO_contrib')
    return LO_evolution_data, LO_summary_stat_data, LO_average_data, CO_average_data, contrib_summary_stat_data, LO_contrib_data
#    i = 0
#    lo_evolution_data = []
#    intermediate_whole_class_lo_data = {LO: [] for LO in df['LO'].unique()}
#    # data for plotting LO averages
#    LO_avg_data = []
#
#    def match_color(val):
#        # SET COLOR TO MATCH MINERVA SCHEME
#        if 0 < val and val < 2:
#            color = '#C83F31'
#        elif 2 <= val and val < 3:
#            color = '#DB883A'
#        elif 3 <= val and val < 4:
#            color = '#56A371'
#        elif 4 <= val and val < 5:
#            color = '#3473B6'
#        elif 5 <= val:
#            color = '#573F88'
#        return color
#    def split_date_func(df):
#        # truncate the Updated Date column so that it contains only the date information
#        df['Updated_Date'] = df['Updated_Date'].str.slice(stop=10)
#
#        # convert to DateTime
#        df['Updated_Date']= pd.to_datetime(df['Updated_Date'])
#    #     print(df[['Updated_Date','LO']])
#        df = df.sort_values(by=['Updated_Date'])
#    #     print(df[['Updated_Date','LO']])
#    #         print('-'*10)
#    #     print(df['Updated_Date'])
#        # summarize the grouped Updated_Date into new columns: 'sum_weighted' and 'tot_weights'
#        df = df.groupby('Updated_Date').apply(lambda x: pd.DataFrame({'sum_weighted': x['weighted_score'].sum(), 
#                                                                 'tot_weights': x['weight'].sum()},
#                                                                index=['Updated_Date'])).reset_index()
#        df = df.drop(['level_1'], axis=1)
#    #     print(df)
#        ###### By this point we have a dataframe with:
#          # * date
#          # * total weighted scores
#          # * total weights
#          # What we want to do is taking the running average up to a certain date
#          # For date #2, it equals: 
#          # A/B where
#          # A is (total weighted scores of date 1 + total weighted scores of date 2)
#          # and B is (total weights of date1 + total weights of date 2)
#
#          ## Idea: we can create 
#          # * a new column (B) that is the cumsum of the vector column total weights
#          # * a new column (A) that is the cumsum of the total weighted scores
#          # * the quantity of interest would be A/B
#        df['cumsum_tot_weights'] = df['tot_weights'].cumsum(axis=0)
#        df['cumsum_sum_weighted'] = df['sum_weighted'].cumsum(axis=0)
#        df['running_avg'] = df['cumsum_sum_weighted'] / df['cumsum_tot_weights']
#    #        print(df)
#        return df
#
#
#    for i in range(num_students):
#        student_name = list_of_students[i]
#        student_df = df[df['Student_Name'] == student_name]
#        # group by LO
#        col_name_to_group_by = 'LO'
#
#        data_with_avg_LO = student_df.groupby(col_name_to_group_by).apply(func=split_date_func)
#        # map LO to CO
#        data_with_avg_LO.reset_index(inplace=True)
#        data_with_avg_LO['CO'] = data_with_avg_LO.apply(lambda row: map_CO(row, LO_IN_ORDER, CO_IN_ORDER), axis=1)
#        agg = {LO: {'visible': False, 'content': []} for LO in data_with_avg_LO['LO'].unique()}
#        for index, row in data_with_avg_LO.iterrows():
#            time_info = (row['Updated_Date'].year, row['Updated_Date'].month-1, row['Updated_Date'].day)
#            if row['LO'] in DEFAULT_LO_TO_DISPLAY_IN_EVOLUTION:
#                visible = True
#            else:
#                visible = False
#            agg[row['LO']]['visible'] = visible
#            agg[row['LO']]['content'].append(['mark',time_info, row['running_avg']])
#
#        series = []    
#        for k, v in agg.items():
#            series.append({'name':k, 
#                           'data': v['content'],
#                           'visible': v['visible']})
#            intermediate_whole_class_lo_data[k].append(v['content'][-1][-1])
#        LO_avg_this_student = {}
#        LO_avg_this_student['student_name'] = student_name
#        LO_avg_this_student['LO'] = []
#        LO_avg_this_student['LO_avg'] = []
#        LO_avg_this_student['color'] = []
#        for LO in series:
#            LO_avg_this_student['LO'].append(LO['name'])
#
#            # SET COLOR TO MATCH MINERVA SCHEME
#            color = match_color(LO['data'][-1][-1])
#            LO_avg_this_student['LO_avg'].append({'y': LO['data'][-1][-1],
#                                                  'color': color})
#    #         LO_avg_this_student['color'].append(color)
#
#
#        LO_avg_data.append(LO_avg_this_student)
#
#        series = str(series).replace("'mark', ", "Date.UTC")
#        series = series.replace("True", 'true')
#        series = series.replace("False", 'false')
#        # add this student's data to data for plotting LO evolution
#        lo_evolution_data.append({'student_name': student_name, 'series': series})
#    # print(lo_evolution_data)
#    # compute summary stats for LO averages for the whole class
#    whole_class_lo_data = {'LO': [], 'mean': [], 'range':[]} 
#    # print(len(intermediate_whole_class_lo_data['pythonimplementation']))
#    for k, v in intermediate_whole_class_lo_data.items():
#        whole_class_lo_data['LO'].append(k)
#        # compute mean
#        mean = np.mean(v)
#        whole_class_lo_data['mean'].append(mean)
#        # compute range
#        min_val = np.min(v)
#        max_val = np.max(v)
#        whole_class_lo_data['range'].append([min_val, max_val])
#
#    
#    CO_avg_data = []
#    for i in range(num_students):
#        student_name = list_of_students[i]
#        student_df = df[df['Student_Name'] == student_name]
#        # group by CO
#        col_name_to_group_by = 'CO'
#
#        data_CO_evolution = student_df.groupby(col_name_to_group_by).apply(func=split_date_func)
#        data_CO_avg = data_CO_evolution.groupby(col_name_to_group_by).tail(1)
#        data_CO_avg.reset_index(inplace=True)
#    #     data_with_avg_CO.reset_index(inplace=True)
#    #     data_with_avg_LO['CO'] = data_with_avg_LO.apply(lambda row: map_CO(row, LO_IN_ORDER, CO_IN_ORDER), axis=1)
#    # data_with_avg_CO.head()
#
#        CO_avg_this_student = {}
#        CO_avg_this_student['student_name'] = student_name
#        CO_avg_this_student['CO'] = []
#        CO_avg_this_student['CO_avg'] = []
#        CO_avg_this_student['color'] = []
#        CO_avg_this_student['course_avg'] = [np.mean(data_CO_avg['running_avg'])]*data_CO_avg.shape[0]
#        for index, row in data_CO_avg.iterrows():
#            CO_avg_this_student['CO'].append(row['CO'])
#            # SET COLOR TO MATCH MINERVA SCHEME
#            color = match_color(row['running_avg'])
#            CO_avg_this_student['CO_avg'].append({'y': row['running_avg'],
#                                                  'color': color})
#        CO_avg_data.append(CO_avg_this_student)
#    
#    # LO contribution
#    intermediate_data_whole_class_LO_contrib = {LO: [] for LO in df['LO'].unique()}
#    LO_contrib_data = []
#    # print(intermediate_data_whole_class_LO_contrib)
#    for i in range(num_students):
#        student_name = list_of_students[i]
#        student_df = df[df['Student_Name'] == student_name]
#        # group by CO
#        col_name_to_group_by = 'CO'
#        data_with_avg_CO = student_df.groupby(col_name_to_group_by).apply(func=split_date_func)
#        data_with_avg_CO = data_with_avg_CO.groupby(col_name_to_group_by).tail(1)
#        data_with_avg_CO.reset_index(inplace=True)
#        num_CO = data_with_avg_CO.shape[0]
#
#        # group by LO
#        col_name_to_group_by = 'LO'
#        data_with_avg_LO = student_df.groupby(col_name_to_group_by).apply(func=split_date_func)
#        data_with_avg_LO = data_with_avg_LO.groupby(col_name_to_group_by).tail(1)
#        data_with_avg_LO.reset_index(inplace=True)
#        # map LO to CO
#        data_with_avg_LO['CO'] = data_with_avg_LO.apply(lambda row: map_CO(row, LO_IN_ORDER, CO_IN_ORDER), axis=1)
#
#        # lookup CO table from LO table
#        data_with_avg_LO = data_with_avg_LO.merge(data_with_avg_CO, on="CO")
#        data_with_avg_LO['LO_contrib'] = data_with_avg_LO['cumsum_sum_weighted_x']/data_with_avg_LO['cumsum_tot_weights_y']/num_CO/np.mean(data_with_avg_CO['running_avg'])
#        for k,v in data_with_avg_LO.iterrows():
#            intermediate_data_whole_class_LO_contrib[v['LO']].append(v['LO_contrib'])
#
#        LO_contrib_data_this_student = {}
#        LO_contrib_data_this_student['LO'] = list(data_with_avg_LO['LO'])
#        LO_contrib_data_this_student['LO_avg'] = list(data_with_avg_LO['LO_contrib'])
#        LO_contrib_data_this_student['student_name'] = student_name
#        LO_contrib_data.append(LO_contrib_data_this_student)
#
#    # compute summary stats for LO averages for the whole class
#    whole_class_lo_contrib_data = {'LO': [], 'mean': [], 'range':[]} 
#    for k, v in intermediate_data_whole_class_LO_contrib.items():
#        whole_class_lo_contrib_data['LO'].append(k)
#        # compute mean
#        mean = np.mean(v)
#        whole_class_lo_contrib_data['mean'].append(mean)
#        # compute range
#        min_val = np.min(v)
#        max_val = np.max(v)
#        whole_class_lo_contrib_data['range'].append([min_val, max_val])

#    return lo_evolution_data, whole_class_lo_data, LO_avg_data, CO_avg_data, whole_class_lo_contrib_data, LO_contrib_data

    