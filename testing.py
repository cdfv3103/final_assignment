import dash_html_components as html
import dash_core_components as dcc
import dash
import pprint as pprint
import pandas as pd
from datetime import datetime
import plotly.express as px
import chart_studio
import chart_studio.plotly as py



# getting the covid-19 data. The data is updated daily
df = pd.read_csv(
    'https://opendata.ecdc.europa.eu/covid19/casedistribution/csv')


# Remove unuseful columns
df = df[['dateRep', 'cases', 'deaths', 'countriesAndTerritories',
         'countryterritoryCode', 'continentExp']]
# Rename columns
df = df.rename(columns={
    'dateRep': 'date',
    'countriesAndTerritories': 'country',
    'countryterritoryCode': 'countryCode',
    'continentExp': 'continent'
})

# Convert string to datetime
df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')

# convert the cases to absolute. might be some negative numbers - this worked after error message
df['cases'] = df['cases'].abs()
df['deaths'] = df['deaths'].abs()

# Preview the data frame
# print(df.sample(10))


# Get today as string
today = datetime.now().strftime('%Y-%m-%d')

# Get a data frame only for today
df_today = df[df.date == today]




# Preview the data frame
# print(df_today.head(10))

# creating map of the cases for today
fig = px.scatter_geo(
    df_today,
    locations='countryCode',
    color='continent',
    hover_name='country',
    size='cases',
    projection="natural earth",
    title=f'World COVID-19 Cases for {today}'
)
# fig.show()


# Convert date to string type
df['date'] = df.date.dt.strftime('%Y%m%d')
# Sort the data frame on date
df = df.sort_values(by=['date'])


# Some countries does not have code, dropping them.
df = df.dropna()

# Preview the data frame
# print(df.head(10))

# creating another map wich animates the spread of the virus
fig2 = px.scatter_geo(
    df,
    locations='countryCode',
    color='continent',
    hover_name='country',
    size='cases',
    projection="natural earth",
    title='World COVID-19 Cases Animation',
    animation_frame="date"
)
# fig.show()



# creating an animated map where we can see how many people die of covid-19
fig3 = px.choropleth(
    df,
    locations="countryCode",
    color="deaths",
    hover_name="country",
    animation_frame="date",
    range_color=[0, 2500]

)




'''
Since the data is in a time-series format, i decided to make accumulated data
so that i can show total deaths and cases.

'''
total_list = df.groupby('countryCode')['deaths'].sum().tolist()
country_list = df["countryCode"].tolist()
country_set = set(country_list)
country_list = list(country_set)
country_list.sort()

new_df = pd.DataFrame(list(zip(country_list, total_list)),
                      columns=['countryCode', 'deaths'])

#print(new_df.head(50))

'''
I wanted to do the same thing for cases, but i could not figure out how to do it in one go.
therefore i repeated the process and joined them.
'''
total_list2 = df.groupby('countryCode')['cases'].sum().tolist()

country_list2 = df["countryCode"].tolist()
country_set2 = set(country_list2)
country_list2 = list(country_set2)
country_list2.sort()

another_df = pd.DataFrame(list(zip(country_list2, total_list2)),
                      columns=['countryCode','cases'])

#merging the datasets
xdf = pd.merge(new_df,another_df,on='countryCode')

#renaming columns
xdf.rename(columns={'deaths':'total_deaths','cases':'accumulated_cases'}, inplace=True)
#print(xdf.head(50))

#merging the dataframe with the original so that i can get country and continent to the final df
final_df = xdf.merge(df_today[['countryCode','country','continent']],on='countryCode',how='left')
#print(final_df.head(50))

#final_df['accumulated_cases'] = final_df['accumulated_cases'].abs()
#final_df['total_deaths'] = final_df['total_deaths'].abs()



fig4 = px.choropleth(
    final_df,
    locations="countryCode",
    color="total_deaths",
    hover_name="country",
    range_color=[0, 80000],
    title=f'Accumulated Covid-19 deaths by country'
    )

#fig4.show()

fig5 = px.scatter_geo(
    final_df,
    locations='countryCode',
    color='continent',
    hover_name='country',
    size='accumulated_cases',
    projection="natural earth",
    title=f'Accumulated COVID-19 Cases by Country',
)

#fig5.show()

#getting css stylesheets
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Initialise the app
app = dash.Dash(__name__,external_stylesheets=external_stylesheets)
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

'''
Note, that when running the app, it takes quite some time.
You will first get a message saying that it is running on http://127.0.0.1:8050/
but it is not done loading. if you wait a second more there will come a second
link that takes you to the app.
'''

# Define the app
app.layout = html.Div(style={'backgroundColor': colors['background']},
    children=[
        html.Div(className='row',
                 children=[
                    html.Div(style={'color':colors['text']},
                            className='four columns div-user-controls',
                             children=[
                                 html.H2('Live Covid-19 Visualization'),
                                 html.P('By scrolling down you can find graphs that you can interact with!'),
                                 html.P('Made By Christian Vedeler'),

                                ]
                             ),
                    html.Div(className='eight columns for maps',
                             children=[
                                dcc.Graph(figure=fig),
                                dcc.Graph(figure=fig2),
                                dcc.Graph(figure=fig3),
                                dcc.Graph(figure=fig4),
                                dcc.Graph(figure=fig5),
                             ])
                              ])
        ]
)


#this website deployment did not work
# data = [fig,fig2,fig3,fig4,fig5]
# chart_studio.tools.set_credentials_file(username='Christ3103', api_key='pebp8XYapzaOmXdnT3QL')
# py.plot(data, filename = 'testing', auto_open=True)



if __name__ == '__main__':
    app.run_server(debug=True)




