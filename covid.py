from flask import Flask, redirect, url_for, render_template,request,jsonify
from flask import send_file, current_app as app
from flask_bootstrap import Bootstrap 
import csv
from bs4 import BeautifulSoup as BS 
import requests 
from covid_india import states
import numpy as np
from numpy import inf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.graph_objs.scatter.marker import Line
from plotly.graph_objs import Line
import matplotlib.pyplot as plt
import IPython
pd.set_option('display.max_columns', None)
import numpy as np 
import pandas as pd
import os
import datetime
from fbprophet import Prophet
from fbprophet.plot import plot_plotly

# import matplotlib
# import matplotlib.pyplot as plt 
# import seaborn as sns
# import warnings
# warnings.filterwarnings('ignore')
# import pandas as pd
# import numpy as np
# import datetime
# import requests
# import warnings

# import matplotlib.dates as mdates
# import seaborn as sns
# import plotly.offline as py
# from IPython.display import Image

app = Flask(__name__)

confirmed_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
deaths_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')
recovered_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')
latest_data = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/04-04-2020.csv')

Bootstrap(app)
@app.route('/')
def home():
    extra_line1=''
    extra_line2=''
    extra_line3=''
    Data = states.getdata('Total')
    State = states.getdata('Karnataka')


    url = "https://www.worldometers.info/coronavirus/"
    data = requests.get(url) 
  
    # converting the text  
    soup = BS(data.text, 'html.parser') 
      
    # finding meta info for total cases 
    total = soup.find("div", class_ = "maincounter-number").text 
      
    # filtering it 
    total = total[1 : len(total) - 2] 
      
    # finding meta info for other numbers 
    other = soup.find_all("span", class_ = "number-table") 
      
    # getting recovered cases number 
    recovered = other[2].text 
      
    # getting death cases number 
    deaths = other[3].text 
      
    # filtering the data 
    deaths = deaths[1:] 
      
    # saving details in dictionary 
    ones = total
    seconds = recovered
    third = deaths
    extra_line1 = f'{ones}'
    extra_line2 = f'{seconds}'
    extra_line3 = f'{third}'
    # print('Total Covid Cases:',data['Total'])
    
    # print('Cured Cases:',data['Cured'])
 
    # print('Death Cases:',data['Death'])
#     extra_line=''
#     def get_info(url):
#         data = requests.get(url) 
  
#     # converting the text  
#         soup = BS(data.text, 'html.parser') 
      
#     # finding meta info for total cases 
#         total = soup.find("div", class_ = "maincounter-number").text 
      
#     # filtering it 
#         total = total[1 : len(total) - 2] 
      
#     # finding meta info for other numbers 
#         other = soup.find_all("span", class_ = "number-table") 
      
#     # getting recovered cases number 
#         recovered = other[2].text 
      
#     # getting death cases number 
#         deaths = other[3].text 
      
#     # filtering the data 
#         deaths = deaths[1:] 
      
#     # saving details in dictionary 
#         ans ={'Total Cases' : total, 'Recovered Cases' : recovered,  
#                                  'Total Deaths' : deaths} 
      
#     # returnng the dictionary 
#         return ans 
#         #
# # url of the corona virus cases 
#     url = "https://www.worldometers.info/coronavirus/"
  
# # calling the get_info method 
#     ans = get_info(url) 
  
# # printing the ans 
#     for i, j in ans.items(): 
#         print(i + " : " + j) 
#         extra_line = f'{ans}'
    
    return render_template("Home.html",data=Data,state=State,new = extra_line1, new1 = extra_line2, new2 = extra_line3)

@app.route('/track',methods=["GET","POST"])
def track():
    Data = None
    State = None
    if request.method =="POST":
        State=request.form['state']
        Data = states.getdata(State) 
    return render_template("track.html",data=Data,state=State)

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/indiaconfirmed')
def indiaconfirmed():
    df = pd.read_csv("Indiajuly21.csv", parse_dates=['Date'], dayfirst=True)
    df = df[['Date', 'State/UnionTerritory','Cured','Deaths','Confirmed']]
    df.columns = ['date', 'state','cured','deaths','confirmed']
    today = df[df.date == '2020-07-24']
    df2 = df.groupby(['date'])['confirmed', 'deaths','cured',].sum().reset_index()
    #making columns for daily new cases
    df2['new_confirmed'] = df2.confirmed.diff()
    df2['new_deaths'] = df2.deaths.diff()
    df2['new_cured'] = df2.cured.diff()
    #taking dates from 15th March
    df2 = df2.iloc[115:]
    #Statewise new confirmed
    df['new_confirmed'] = df.groupby(['state'])['confirmed'].diff()
    df['new_deaths'] = df.groupby(['state'])['deaths'].diff()
    df['new_cured'] = df.groupby(['state'])['cured'].diff()
    df3 = df2[['date' , 'confirmed']]
    #Renaming column names according to fb prophet
    df3.columns = ['ds' , 'y']
    m = Prophet()
    m.fit(df3)
    future = m.make_future_dataframe(periods= 10) 
    forecast = m.predict(future)
    fig = plot_plotly(m, forecast)  # This returns a plotly Figure
    fig.update_layout(
        title_text='<b>Covid-19 Total cases Forecast<b>',
        title_x=0.5,
        paper_bgcolor='LightBlue',
        plot_bgcolor = "LightBlue",)
    fig.show()
    return render_template("indiastatistics.html")

@app.route('/indiacured')
def indiacured():
    df = pd.read_csv("Indiajuly21.csv", parse_dates=['Date'], dayfirst=True)
    df = df[['Date', 'State/UnionTerritory','Cured','Deaths','Confirmed']]
    df.columns = ['date', 'state','cured','deaths','confirmed']
    today = df[df.date == '2020-07-24']
    df2 = df.groupby(['date'])['confirmed', 'deaths','cured',].sum().reset_index()
    #making columns for daily new cases
    df2['new_confirmed'] = df2.confirmed.diff()
    df2['new_deaths'] = df2.deaths.diff()
    df2['new_cured'] = df2.cured.diff()
    #taking dates from 15th March
    df2 = df2.iloc[64:]
    #Statewise new confirmed
    df['new_confirmed'] = df.groupby(['state'])['confirmed'].diff()
    df['new_deaths'] = df.groupby(['state'])['deaths'].diff()
    df['new_cured'] = df.groupby(['state'])['cured'].diff()
    df3 = df2[['date' , 'cured']]
    #Renaming column names according to fb prophet
    df3.columns = ['ds' , 'y']
    m = Prophet()
    m.fit(df3)
    future = m.make_future_dataframe(periods= 10) 
    forecast = m.predict(future)
    fig = plot_plotly(m, forecast)  # This returns a plotly Figure
    fig.update_layout(
        title_text='<b>Covid-19 Total Recoveries cases Forecast<b>',
        title_x=0.5,
        paper_bgcolor='LightGreen',
        plot_bgcolor = "LightGreen",)
    fig.show()
    return render_template("indiastatistics.html")

@app.route('/indiadeaths')
def indiadeaths():
    df = pd.read_csv("Indiajuly21.csv", parse_dates=['Date'], dayfirst=True)
    df = df[['Date', 'State/UnionTerritory','Cured','Deaths','Confirmed']]
    df.columns = ['date', 'state','cured','deaths','confirmed']
    today = df[df.date == '2020-07-24']
    df2 = df.groupby(['date'])['confirmed', 'deaths','cured',].sum().reset_index()
    #making columns for daily new cases
    df2['new_confirmed'] = df2.confirmed.diff()
    df2['new_deaths'] = df2.deaths.diff()
    df2['new_cured'] = df2.cured.diff()
    #taking dates from 15th March
    df2 = df2.iloc[64:]
    #Statewise new confirmed
    df['new_confirmed'] = df.groupby(['state'])['confirmed'].diff()
    df['new_deaths'] = df.groupby(['state'])['deaths'].diff()
    df['new_cured'] = df.groupby(['state'])['cured'].diff()
    df3 = df2[['date' , 'deaths']]
    #Renaming column names according to fb prophet
    df3.columns = ['ds' , 'y']
    m = Prophet()
    m.fit(df3)
    future = m.make_future_dataframe(periods= 10) 
    forecast = m.predict(future)
    fig = plot_plotly(m, forecast)  # This returns a plotly Figure
    fig.update_layout(
        title_text='<b>Covid-19 Total deaths cases Forecast<b>',
        title_x=0.5,
        paper_bgcolor='LightCoral',
        plot_bgcolor = "LightCoral",)
    fig.show()
    return render_template("indiastatistics.html")

@app.route('/remedies',methods=["GET","POST"])
def remedies():
    result = None
    extra_line=''
    if request.method =="POST":
        Districts=request.form['districts']
        data =[]
        with open("helpline.csv") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                data.append(row)
        col = [x[1] for x in data]
        if Districts in col:
            for x in range(0,len(data)):
                if Districts == data[x][1]:
                    result = data[x][2]
                    print(result)
        else:
            print('Does not exist')
        extra_line = f'Call  :"{result}"'
    return render_template("Remedies.html",new = extra_line)

@app.route('/Symptoms')
def Symptoms():
    return render_template("Symptoms.html")


@app.route('/Hospital')
def Hospital():
    return render_template("Hospital.html")


@app.route('/HospitalBangalore')
def HospitalBangalore():
    return render_template("HospitalBangalore.html")

@app.route('/predict')
def predict():
    return render_template("predict.html")

@app.route('/karnatakaconfirmed')
def karnatakaconfirmed():
    df = pd.read_csv("onlykarnatakajune3.csv", parse_dates=['Date'], dayfirst=True)
    df = df[['Date', 'State/UnionTerritory','Cured','Deaths','Confirmed']]
    df.columns = ['date', 'state','cured','deaths','confirmed']
    #df.isna().sum()
    today = df[df.date == '2020-07-24']
    df2 = df.groupby(['date'])['confirmed', 'deaths','cured',].sum().reset_index()
    #making columns for daily new cases
    df2['new_confirmed'] = df2.confirmed.diff()
    df2['new_deaths'] = df2.deaths.diff()
    df2['new_cured'] = df2.cured.diff()
    #taking dates from 15th March
    df2 = df2.iloc[100:]
    #Statewise new confirmed
    df['new_confirmed'] = df.groupby(['state'])['confirmed'].diff()
    df['new_deaths'] = df.groupby(['state'])['deaths'].diff()
    df['new_cured'] = df.groupby(['state'])['cured'].diff()
    fig = px.line(df, x="date", y="confirmed", color='state',template= "plotly_white")
    fig.update_xaxes(tickfont=dict(family='Rockwell', color='black', size=14))
    fig.update_yaxes(tickfont=dict(family='Rockwell', color='black', size=14))
    fig.update_traces(mode='markers')
    fig.update_layout(
        title_text='<b>Confirmed Cases of Covid-19 in Karnataka<b> ',
        title_x=0.5,
        paper_bgcolor='snow',
        plot_bgcolor = "snow")
    fig.show()
    return render_template("karnataka.html")

@app.route('/karconfirmed')
def karconfirmed():
    df = pd.read_csv("onlykarnatakajune3.csv", parse_dates=['Date'], dayfirst=True)
    df = df[['Date', 'State/UnionTerritory','Cured','Deaths','Confirmed']]
    df.columns = ['date', 'state','cured','deaths','confirmed']
    #df.isna().sum()
    today = df[df.date == '2020-07-24']
    df2 = df.groupby(['date'])['confirmed', 'deaths','cured',].sum().reset_index()
    #making columns for daily new cases
    df2['new_confirmed'] = df2.confirmed.diff()
    df2['new_deaths'] = df2.deaths.diff()
    df2['new_cured'] = df2.cured.diff()
    #taking dates from 15th March
    df2 = df2.iloc[126:]
    #Statewise new confirmed
    df['new_confirmed'] = df.groupby(['state'])['confirmed'].diff()
    df['new_deaths'] = df.groupby(['state'])['deaths'].diff()
    df['new_cured'] = df.groupby(['state'])['cured'].diff()
    df3 = df2[['date' , 'confirmed']]

    #Renaming column names according to fb prophet
    df3.columns = ['ds' , 'y']
    m = Prophet()
    m.fit(df3)
    future = m.make_future_dataframe(periods= 10) 
    forecast = m.predict(future)
    #forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(31)
    fig = plot_plotly(m, forecast)  # This returns a plotly Figure
    fig.update_layout(
        title_text='<b>Covid-19 Total cases Forecast in karnataka<b>',
        title_x=0.5,
        paper_bgcolor='LightBlue',
        plot_bgcolor = "LightBlue",)
    fig.show()
    return render_template("karnataka.html")



@app.route('/karcured')
def karcured():
    df = pd.read_csv("onlykarnatakajune3.csv", parse_dates=['Date'], dayfirst=True)
    df = df[['Date', 'State/UnionTerritory','Cured','Deaths','Confirmed']]
    df.columns = ['date', 'state','cured','deaths','confirmed']
    #df.isna().sum()
    today = df[df.date == '2020-07-24']
    df2 = df.groupby(['date'])['confirmed', 'deaths','cured',].sum().reset_index()
    #making columns for daily new cases
    df2['new_confirmed'] = df2.confirmed.diff()
    df2['new_deaths'] = df2.deaths.diff()
    df2['new_cured'] = df2.cured.diff()
    #taking dates from 15th March
    df2 = df2.iloc[122:]
    #Statewise new confirmed
    df['new_confirmed'] = df.groupby(['state'])['confirmed'].diff()
    df['new_deaths'] = df.groupby(['state'])['deaths'].diff()
    df['new_cured'] = df.groupby(['state'])['cured'].diff()
    df3 = df2[['date' , 'cured']]

    #Renaming column names according to fb prophet
    df3.columns = ['ds' , 'y']
    m = Prophet()
    m.fit(df3)
    future = m.make_future_dataframe(periods= 10) 
    forecast = m.predict(future)
    #forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(31)
    fig = plot_plotly(m, forecast)  # This returns a plotly Figure
    fig.update_layout(
        title_text='<b>Covid-19 Total Recovery cases Forecast in karnataka<b>',
        title_x=0.5,
        paper_bgcolor='LightGreen',
        plot_bgcolor = "LightGreen",)
    fig.show()
    return render_template("karnataka.html")



@app.route('/kardeaths')
def kardeaths():
    df = pd.read_csv("onlykarnatakajune3.csv", parse_dates=['Date'], dayfirst=True)
    df = df[['Date', 'State/UnionTerritory','Cured','Deaths','Confirmed']]
    df.columns = ['date', 'state','cured','deaths','confirmed']
    #df.isna().sum()
    today = df[df.date == '2020-07-24']
    df2 = df.groupby(['date'])['confirmed', 'deaths','cured',].sum().reset_index()
    #making columns for daily new cases
    df2['new_confirmed'] = df2.confirmed.diff()
    df2['new_deaths'] = df2.deaths.diff()
    df2['new_cured'] = df2.cured.diff()
    #taking dates from 15th March
    df2 = df2.iloc[122:]
    #Statewise new confirmed
    df['new_confirmed'] = df.groupby(['state'])['confirmed'].diff()
    df['new_deaths'] = df.groupby(['state'])['deaths'].diff()
    df['new_cured'] = df.groupby(['state'])['cured'].diff()
    df3 = df2[['date' , 'deaths']]

    #Renaming column names according to fb prophet
    df3.columns = ['ds' , 'y']
    m = Prophet()
    m.fit(df3)
    future = m.make_future_dataframe(periods= 10) 
    forecast = m.predict(future)
    #forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(31)
    fig = plot_plotly(m, forecast)  # This returns a plotly Figure
    fig.update_layout(
        title_text='<b>Covid-19 Total Deaths cases Forecast in karnataka<b>',
        title_x=0.5,
        paper_bgcolor='LightCoral',
        plot_bgcolor = "LightCoral",)
    fig.show()
    return render_template("karnataka.html")

@app.route('/indiastatistics')
def indiastatistics():
    return render_template("indiastatistics.html")

@app.route('/karnataka')
def karnataka():
    return render_template("karnataka.html")

@app.route('/worldwidestatistics')
def worldwidestatistics():
    return render_template('worldwidestatistics.html')
    
@app.route('/visualization')
def visualization():
    return render_template("visualization.html")

@app.route('/Recovered')
def Recovered():
    corona_data1=pd.read_csv('covid_19_data.csv')
    choro_map=px.choropleth(corona_data1, 
                    locations="Country/Region", 
                    locationmode = "country names",
                    color="Recovered", 
                    hover_name="Country/Region", 
                    animation_frame="ObservationDate"
                   )

    choro_map.update_layout(
        title_text = 'WorldWide Recoveries',
        title_x = 0.5,
        geo=dict(
            showframe = False,
            showcoastlines = False,
    ))
    
    choro_map.show()
    extra_line1=''
    extra_line2=''
    extra_line3=''
    Data = states.getdata('Total')
    State = states.getdata('Karnataka')


    url = "https://www.worldometers.info/coronavirus/"
    data = requests.get(url) 
  
    # converting the text  
    soup = BS(data.text, 'html.parser') 
      
    # finding meta info for total cases 
    total = soup.find("div", class_ = "maincounter-number").text 
      
    # filtering it 
    total = total[1 : len(total) - 2] 
      
    # finding meta info for other numbers 
    other = soup.find_all("span", class_ = "number-table") 
      
    # getting recovered cases number 
    recovered = other[2].text 
      
    # getting death cases number 
    deaths = other[3].text 
      
    # filtering the data 
    deaths = deaths[1:] 
      
    # saving details in dictionary 
    ones = total
    seconds = recovered
    third = deaths
    extra_line1 = f'{ones}'
    extra_line2 = f'{seconds}'
    extra_line3 = f'{third}'
    return render_template("Home.html",data=Data,state=State,new = extra_line1, new1 = extra_line2, new2 = extra_line3)


@app.route('/death')
def death():
    corona_data1=pd.read_csv('covid_19_data.csv')
    choro_map=px.choropleth(corona_data1, 
                    locations="Country/Region", 
                    locationmode = "country names",
                    color="Deaths", 
                    hover_name="Country/Region", 
                    animation_frame="ObservationDate"
                   )

    choro_map.update_layout(
    title_text = 'WorldWide Deaths caused by Coronavirus',
    title_x = 0.5,
    geo=dict(
        showframe = False,
        showcoastlines = False,
    ))
    
    choro_map.show()
    extra_line1=''
    extra_line2=''
    extra_line3=''
    Data = states.getdata('Total')
    State = states.getdata('Karnataka')


    url = "https://www.worldometers.info/coronavirus/"
    data = requests.get(url) 
  
    # converting the text  
    soup = BS(data.text, 'html.parser') 
      
    # finding meta info for total cases 
    total = soup.find("div", class_ = "maincounter-number").text 
      
    # filtering it 
    total = total[1 : len(total) - 2] 
      
    # finding meta info for other numbers 
    other = soup.find_all("span", class_ = "number-table") 
      
    # getting recovered cases number 
    recovered = other[2].text 
      
    # getting death cases number 
    deaths = other[3].text 
      
    # filtering the data 
    deaths = deaths[1:] 
      
    # saving details in dictionary 
    ones = total
    seconds = recovered
    third = deaths
    extra_line1 = f'{ones}'
    extra_line2 = f'{seconds}'
    extra_line3 = f'{third}'
    return render_template("Home.html",data=Data,state=State,new = extra_line1, new1 = extra_line2, new2 = extra_line3)


@app.route('/world')
def world():
    corona_data=pd.read_csv('covid_19_data.csv')
    choro_map=px.choropleth(corona_data, 
                    locations="Country/Region", 
                    locationmode = "country names",
                    color="Confirmed", 
                    hover_name="Country/Region", 
                    animation_frame="ObservationDate"
                   )

    choro_map.update_layout(
        title_text = 'WorldWide Spread of Coronavirus',
        title_x = 0.5,
        geo=dict(
            showframe = False,
            showcoastlines = False,
    ))
    
    choro_map.show()
    extra_line1=''
    extra_line2=''
    extra_line3=''
    Data = states.getdata('Total')
    State = states.getdata('Karnataka')


    url = "https://www.worldometers.info/coronavirus/"
    data = requests.get(url) 
  
    # converting the text  
    soup = BS(data.text, 'html.parser') 
      
    # finding meta info for total cases 
    total = soup.find("div", class_ = "maincounter-number").text 
      
    # filtering it 
    total = total[1 : len(total) - 2] 
      
    # finding meta info for other numbers 
    other = soup.find_all("span", class_ = "number-table") 
      
    # getting recovered cases number 
    recovered = other[2].text 
      
    # getting death cases number 
    deaths = other[3].text 
      
    # filtering the data 
    deaths = deaths[1:] 
      
    # saving details in dictionary 
    ones = total
    seconds = recovered
    third = deaths
    extra_line1 = f'{ones}'
    extra_line2 = f'{seconds}'
    extra_line3 = f'{third}'
    return render_template("Home.html",data=Data,state=State,new = extra_line1, new1 = extra_line2, new2 = extra_line3)





if __name__ == "__main__":
    app.run(debug=True)