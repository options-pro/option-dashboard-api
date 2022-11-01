from xmlrpc.client import ResponseError
from django.http import JsonResponse
from datetime import date
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import pandas as pd
import csv ,operator ,json
import os
import glob

@api_view(['GET'])
def tickeroi(request,ticker):

    ticker = ticker.upper()
    today = date.today()
    date1 = today.strftime("%d")
    month = (today.strftime("%B")[0:3]).capitalize()
    year = today.strftime("%Y")
    d1 = date1+month+year

    path = os.getcwd()+'/market/'
    # location = path + "fo"+d1+"bhav.csv"
    location = path + 'fo01oct2022bhav.csv'
    dfce = pd.read_csv(location)
    dfpe = pd.read_csv(location)

    dfce = dfce.loc[dfce['INSTRUMENT']=='OPTSTK']
    dfpe = dfpe.loc[dfpe['INSTRUMENT']=='OPTSTK']

    dfce = dfce.loc[dfce['OPTION_TYP']=='CE']
    dfpe = dfpe.loc[dfpe['OPTION_TYP']=='PE']

    dfce = dfce.loc[dfce['SYMBOL']==ticker]
    dfpe = dfpe.loc[dfpe['SYMBOL']==ticker]
    dfce = dfce.groupby(['STRIKE_PR']).sum()
    dfpe = dfpe.groupby(['STRIKE_PR']).sum()

    dfce['OPTION_TYP'] = 'CE'
    dfpe['OPTION_TYP'] = 'PE'

    cols = [0,1,2,3,4,5,6,8,9]
    dfce.drop(dfce.columns[cols],axis=1,inplace=True)
    dfpe.drop(dfpe.columns[cols],axis=1,inplace=True)

    dfce['STRIKE_PR'] = dfce.index
    dfpe['STRIKE_PR'] = dfpe.index

    df = pd.concat([dfce, dfpe],ignore_index=True)

    dfce.reset_index(drop = True, inplace = True)
    dfpe.reset_index(drop = True, inplace = True)

    df = pd.merge(dfce,dfpe,on='STRIKE_PR')
    df['SYMBOL'] = ticker
    df.rename(columns = {'OPEN_INT_x':'OPEN_INT_CE', 'OPEN_INT_y':'OPEN_INT_PE'}, inplace = True)
    cols = [1,4]
    df.drop(df.columns[cols],axis=1,inplace=True)

    df = df[df['OPEN_INT_CE'] != 0]
    df = df[df['OPEN_INT_PE'] != 0]
    df = df.reset_index(drop=True)

    if request.method == 'GET':
        jsonData = df.to_json(orient='records')
        jsonData = json.loads(jsonData) 
        return Response(jsonData)