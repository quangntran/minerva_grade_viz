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

def index(request):
    # r = requests.get('http://httpbin.org/status/418')
    # print(r.text)
    # return HttpResponse('<pre>' + r.text + '</pre>')
    context = {'Tokyo': [7.0, 6.9, 9.5, 14.5, 18.2, 21.5, 25.2, 40, 23.3, 18.3, 13.9, 9.6]}
    return render(request, "index.html", context)

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

def upload(request):
    if request.method == "POST":
        uploaded_file = request.FILES['document']
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
        lo_evolution_data, whole_class_lo_data, LO_avg_data, CO_avg_data = process_df(df)
        return render(request, 'view_chart.html', {'lo_evolution_data': lo_evolution_data,
                                                   'whole_class_lo_data': whole_class_lo_data,
                                                   'LO_avg_data': LO_avg_data,
                                                   'CO_avg_data': CO_avg_data})
         
    return render(request, 'upload.html')