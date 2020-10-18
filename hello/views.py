from django.shortcuts import render
from django.http import HttpResponse
#from django.utils import simplejson

from .models import Greeting
import requests
#from django.core.files.storage import FileSystemStorage
import pandas as pd
import io
from .data_process import process_df
import json
# Create your views here.
import json
from pytz import utc 
import datetime
from json import JSONEncoder
from .forms import GradeForm

def index(request):
    if request.method == "POST":
        form = GradeForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            LO_IN_ORDER = list(map(lambda x: x.strip(), form.cleaned_data['lo_list'].split(','), ))
            CO_IN_ORDER = list(map(lambda x: x.strip(), form.cleaned_data['co_list'].split(','), ))
            ASSIGNMENT_TITLES = list(map(lambda x: x.strip(), form.cleaned_data['assignment_title'].split(','), ))
            ASSIGNMENT_WEIGHTS = list(map(lambda x: int(x.strip()), form.cleaned_data['assignment_weight'].split(','), ))
            DEFAULT_LO_TO_DISPLAY_IN_EVOLUTION = list(map(lambda x: x.strip(), form.cleaned_data['default_lo'].split(','), ))
            params = {'LO_IN_ORDER': LO_IN_ORDER, 'CO_IN_ORDER': CO_IN_ORDER, 
                      'ASSIGNMENT_TITLES': ASSIGNMENT_TITLES, 'ASSIGNMENT_WEIGHTS': ASSIGNMENT_WEIGHTS, 'DEFAULT_LO_TO_DISPLAY_IN_EVOLUTION': DEFAULT_LO_TO_DISPLAY_IN_EVOLUTION, }
            df = pd.read_csv(io.StringIO(uploaded_file.read().decode('utf-8')), delimiter=',')
            LO_evolution_data, LO_summary_stat_data, LO_average_data, CO_average_data, contrib_summary_stat_data, LO_contrib_data = process_df(df, params)
            return render(request, 'view_chart.html', {'LO_evolution_data': LO_evolution_data, 
                                                       'LO_summary_stat_data': LO_summary_stat_data, 
                                                       'LO_average_data': LO_average_data, 
                                                       'CO_average_data': CO_average_data, 'contrib_summary_stat_data': contrib_summary_stat_data, 
                                                       'LO_contrib_data': LO_contrib_data})
    else:   
        form = GradeForm()
        return render(request, "index.html", {'form': form})

def view_teapot(request):
    context = {'data': [
                       {'y': 107, 'color':'red'},
                       {'y':31, 'color':'red'},
                       {'y':635},
                       {'y':203, 'color':'green'},
                       {'y':2}
                   ],
              'LO_list': ['lo1', 'lo2', 'lo3', 'lo4', 'lo5']}
    return render(request, "chart.html", context)
    
def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()
    return render(request, "db.html", {"greetings": greetings})

#  file = forms.FileField(label='Upload file')
#    lo_list = forms.CharField(label='LO list', max_length=500)
#    co_list = forms.CharField(label='CO list', max_length=500)
#    assignment_title = forms.CharField(label='Assignment titles', max_length=500)
#    assignment_weight = forms.CharField(label='Assignment weights', max_length=500)
#    default_lo = forms.CharField(label='LO to highlight in LO evolution graph', max_length=500)
#    

#LO_IN_ORDER = ["mcanalysis", "mcmodeling", "interpretresults", "professionalism", "pythonimplementation","caanalysis", "camodeling", "networkanalysis","networkmodeling"]
#CO_IN_ORDER = ["MonteCarlo","MonteCarlo","Simulations","Simulations","Simulations","Cellular Automata","Cellular Automata","Networks","Networks"]
#ASSIGNMENT_TITLES =  ["Elevator simulation",
#                        "Traffic simulation",
#                        "Network simulation",
#                        'Final project proposal',
#                        "Final project"]
#ASSIGNMENT_WEIGHTS = [2, 6, 6, 0, 10]
#DEFAULT_LO_TO_DISPLAY_IN_EVOLUTION = ['networkanalysis', 'networkmodeling']

def upload(request):
    if request.method == "POST":
        form = GradeForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            LO_IN_ORDER = list(map(lambda x: x.strip(), form.cleaned_data['lo_list'].split(','), ))
            CO_IN_ORDER = list(map(lambda x: x.strip(), form.cleaned_data['co_list'].split(','), ))
            ASSIGNMENT_TITLES = list(map(lambda x: x.strip(), form.cleaned_data['assignment_title'].split(','), ))
            ASSIGNMENT_WEIGHTS = list(map(lambda x: int(x.strip()), form.cleaned_data['assignment_weight'].split(','), ))
            DEFAULT_LO_TO_DISPLAY_IN_EVOLUTION = list(map(lambda x: x.strip(), form.cleaned_data['default_lo'].split(','), ))
            params = {'LO_IN_ORDER': LO_IN_ORDER, 'CO_IN_ORDER': CO_IN_ORDER, 
                      'ASSIGNMENT_TITLES': ASSIGNMENT_TITLES, 'ASSIGNMENT_WEIGHTS': ASSIGNMENT_WEIGHTS, 'DEFAULT_LO_TO_DISPLAY_IN_EVOLUTION': DEFAULT_LO_TO_DISPLAY_IN_EVOLUTION, }
    #        fs = FileSystemStorage()
    #        fs.save(uploaded_file.name, uploaded_file)
            df = pd.read_csv(io.StringIO(uploaded_file.read().decode('utf-8')), delimiter=',')
            
    #        data_with_avg_LO = process_df(df)
    #        def convert_timestamp(item_date_object):
    #            if isinstance(item_date_object, (datetime.date, datetime.datetime)):
    #                return item_date_object.timestamp()
    #            
    #        agg = {LO: [] for LO in data_with_avg_LO['LO'].unique()}
    #        for index, row in data_with_avg_LO.iterrows():
    #            agg[row['LO']].append([row['Updated_Date'], row['running_avg']])
    #        series = []    
    #        for k, v in agg.items():
    #            series.append({'name':k, 
    #                           'data': v})
    #        context = series

    #### works but with hours
    #        agg = {LO: [] for LO in data_with_avg_LO['LO'].unique()}
    #        for index, row in data_with_avg_LO.iterrows():
    #            agg[row['LO']].append([row['Updated_Date'], row['running_avg']])
    #        series = []    
    #        for k, v in agg.items():
    #            series.append({'name':k, 
    #                           'data': v})
    #        series = json.dumps(series, default=convert_timestamp)
    ##########        
    #        class DateTimeEncoder(JSONEncoder):
    #                #Override the default method
    #                def default(self, obj):
    #                    if isinstance(obj, (datetime.date, datetime.datetime)):
    #                        return obj.isoformat()
    #
    #        agg = {LO: [] for LO in data_with_avg_LO['LO'].unique()}
    #        for index, row in data_with_avg_LO.iterrows():
    #        #     time_info = [row['Updated_Date'].year, row['Updated_Date'].month, row['Updated_Date'].day]
    #            agg[row['LO']].append([row['Updated_Date'], row['running_avg']])
    #        series = []    
    #        for k, v in agg.items():
    #            series.append({'name':k, 
    #                           'data': v})
    #        # json.dumps(series)
    #        series = json.dumps(series, indent=4, cls=DateTimeEncoder)
    #        agg = {LO: [] for LO in data_with_avg_LO['LO'].unique()}
    #        for index, row in data_with_avg_LO.iterrows():
    #            time_info = (row['Updated_Date'].year, row['Updated_Date'].month-1, row['Updated_Date'].day)
    #            agg[row['LO']].append(['mark',time_info, row['running_avg']])
    #        series = []    
    #        for k, v in agg.items():
    #            series.append({'name':k, 
    #                           'data': v})
    #        series = str(series).replace("'mark', ", "Date.UTC")
            LO_evolution_data, LO_summary_stat_data, LO_average_data, CO_average_data, contrib_summary_stat_data, LO_contrib_data = process_df(df, params)
#            print(contrib_summary_stat_data)
            return render(request, 'view_chart.html', {'LO_evolution_data': LO_evolution_data, 
                                                       'LO_summary_stat_data': LO_summary_stat_data, 
                                                       'LO_average_data': LO_average_data, 
                                                       'CO_average_data': CO_average_data, 'contrib_summary_stat_data': contrib_summary_stat_data, 
                                                       'LO_contrib_data': LO_contrib_data})
    else:
        form = GradeForm()
    return render(request, 'upload.html', {'form': form})