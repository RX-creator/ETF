import streamlit as st
import pandas as pd
import pandas_datareader as web
import numpy as np
from datetime import datetime, date
import matplotlib.pyplot as plt
import plotly.express as px
import altair as alt
#%matplotlib inline

#Title
st.title('ETF - Beispiel')


#Create all ticker symbols and names
symbol_list = ['EUNL.DE', 'IS3N.DE']
names_list = ['MSCI World', 'MSCI Emerging Markets']


#Creating a radio to choose the tickers from
etf_option = str(st.sidebar.radio('Wähle einen ETF aus', names_list))
a = names_list.index(etf_option)

#Define a long period of time for dataframe
start_first = datetime.date(datetime(1990, 1, 1))
end_first = datetime.today()

#Creating a empty Dataframe to store the data inside
df = pd.DataFrame()
df[etf_option] = web.DataReader(symbol_list[a], data_source = "yahoo", start=start_first, end=end_first)["Adj Close"]

#Find the start date
new_start = df.first_valid_index()


#Setting start and end date with the datetime module
start_date = st.sidebar.date_input("Start Datum", value = datetime.date(datetime(2018, 1, 1)), min_value = new_start)
end_date = st.sidebar.date_input("End Datum", value= datetime.today(), min_value = new_start, max_value = datetime.today()) 

#
start_year = start_date.strftime("%Y")
start_month = start_date.strftime("%m")
start_day = start_date.strftime("%d")


#Define date for first buying
if start_day in range(6,32):
    start_day = 1
    if start_month == 12:
        start_month = 1
        start_year = start_year + 1
    else:
        start_month = start_month + 1


#Download data in TimePeriod
df[etf_option] = web.DataReader(symbol_list[a], data_source = "yahoo", start=start_date, end=end_date)["Adj Close"]


#Create new rows in dataframe
df['Eingezahlt'] = pd.Series()
df['Anteile'] = pd.Series()
df['Depotwert'] = pd.Series()
df['Durchschnittspreis'] = pd.Series()


#Transform datatime in int
year = int(start_year)
month = int(start_month)
day = int(start_day)

#Create the saving plan
zahlrate = st.sidebar.number_input('Wie hoch beträgt deine monatliche Sparrate in €?', 25, 10000, 100)
zaehler = 1
anteile = 0
durchschnitt = 0

#fill with data
while pd.isna(df['Eingezahlt'].iloc[-1]):
    if month in range(1,10):
        df["Eingezahlt"].loc[str(year)+'-0' + str(month)] = zahlrate * zaehler
        df["Durchschnittspreis"].loc[str(year)+'-0' + str(month)] = (df[etf_option].loc[str(year)+'-0' + str(month)].iloc[0] + durchschnitt) / zaehler
        durchschnitt = durchschnitt + df[etf_option].loc[str(year)+'-0' + str(month)].iloc[0]
        anteile = zahlrate / df[etf_option].loc[str(year)+'-0' + str(month)].iloc[0] + anteile
        df["Anteile"].loc[str(year)+'-0' + str(month)] = anteile
    else:
        df["Eingezahlt"].loc[str(year)+'-' + str(month)] = zahlrate * zaehler
        df["Durchschnittspreis"].loc[str(year)+'-' + str(month)] = (df[etf_option].loc[str(year)+'-' + str(month)].iloc[0] + durchschnitt) / zaehler
        durchschnitt = durchschnitt + df[etf_option].loc[str(year)+'-' + str(month)].iloc[0]
        anteile = zahlrate / df[etf_option].loc[str(year)+'-' + str(month)].iloc[0] + anteile
        df["Anteile"].loc[str(year)+'-' + str(month)] = anteile
    
    
            
    zaehler = zaehler + 1
    if month == 12:
        month = 1
        year = year + 1
    else:
        month = month + 1


df['Depotwert'] = df[etf_option] * df['Anteile']


#First plot
#st.subheader('Kursverlauf und Durchschnittspreis')
#fig = plt.figure(figsize=(16,8))
#plt.plot(df[etf_option])
#plt.plot(df['Durchschnittspreis'], 'g--')
#plt.grid()
#st.pyplot(fig)

#plot with plotly
df1 = pd.DataFrame()
df1 = df.loc[start_date:end_date]
fig4 = px.line(df1, y=[etf_option, 'Durchschnittspreis'], width=850, height=400, render_mode="svg")
fig4.update_traces(line=dict(width=1.2))
st.subheader('Kursverlauf und Durchschnittspreis')
st.plotly_chart(fig4)


#Second plot
st.subheader('Einzahlungen und Depotwert')
fig2 = plt.figure(figsize=(16,8))
plt.plot(df['Eingezahlt'])
plt.plot(df['Depotwert'])
plt.grid()
st.pyplot(fig2)

#Third plot
st.subheader('Maximaler Gewinn und Verlust')
fig3 = plt.figure(figsize=(16,8))
plt.plot(df['Depotwert'] - df['Eingezahlt'])
plt.axhline(y=0, color = 'b')
plt.axhline(y=(df['Depotwert'] - df['Eingezahlt']).max(), color = 'g')
plt.axhline(y=(df['Depotwert'] - df['Eingezahlt']).min(), color = 'r')
plt.grid()
st.pyplot(fig3)

max = (df['Depotwert'] - df['Eingezahlt']).max()
max = "%.2f" % max
min = (df['Depotwert'] - df['Eingezahlt']).min()
min = "%.2f" % min
st.text('Maximaler Gewinn: ' + max + '€')
st.text('Maximaler Verlust: ' + min + '€')