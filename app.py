# %%
# import dependencies
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# %%
# read in csv file & view first 5 rows
df = pd.read_csv("gdp_pcap.csv")
df.head()

# %%
stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'] # load the CSS stylesheet

app = Dash(__name__, external_stylesheets=stylesheets) # initialize the app
server=app.server

# %%
# pivot table to organize by country, years, and gdpPerCapita
countryPerCap = df.melt(id_vars = 'country', 
                          value_vars = df.columns[1:],  #extracts first row of years
                          var_name = 'year',
                          value_name = 'gdpPercap')

# Convert 'gdpPercap' column to numeric
countryPerCap['gdpPercap'] = pd.to_numeric(countryPerCap['gdpPercap'], errors='coerce')

# Drop rows with na's
countryPerCap = countryPerCap.dropna(subset=['gdpPercap'])

# Sort the pivot table by GDP per Capita
countryPerCap_sorted = countryPerCap.sort_values(by=['year', 'gdpPercap'])

# build a line chart using pivot table
fig_line_color = px.line(countryPerCap_sorted, 
                      x = 'year', 
                      y = 'gdpPercap',
                      color = 'country',
                      title = 'GDP per Capita by Country Through the Years')

# %%
years = df.columns[1:]   #set aside this list for the years

app.layout = html.Div([    
    html.H1("GDP Analysis Dashboard"),  #Header for title
    html.P("This data analyzes the GDP per Capita of different countries over time. To use the app, first select the countries you want to study. Then, select the range of years you want to look at. The final component shows a line chart of different countries GDP capita through the years."), #description under title
        dcc.Dropdown(      #use dcc to create dropdown menu
        id='country-dropdown',      #ID tag for dropdown
        options=[{'label': country, 'value': country} for country in df['country']],   #specifies to go through each country in the dataframe as the options for the dropdown
        multi=True,     #allows to click multiple countries
        placeholder="Select Countries",     #name of the dropdown before countries are selected
        className="six columns"          #formats dropdown to be on left half of screen
    ),
    

    dcc.RangeSlider(    #use dcc to create range slider 
        id='year-slider',  #ID tag for range slider
        marks={year: str(year) for year in range(int(min(years)), int(max(years))+1, 50)},  #shows markings on slider as minimum and maximum years from the dataframe
        min=int(min(years)),   #minimum as minimum from df years list
        max=int(max(years)),    #maximum as maximum from df years list
        step=1,   #steps up by 1
        value=[int(min(years)), int(max(years))],   
        className="six columns"   #formats range slider to be on right half of screen
    ),
    dcc.Graph(   #use dcc to greate graph that uses the plotly line chart from above
        id='gdp-line-chart',
        figure=fig_line_color,
        className="twelve columns"
    )
]

,className="row")

@app.callback(
    Output('gdp-line-chart', 'figure'),
    [Input('country-dropdown', 'value'),
     Input('year-slider', 'value')]
)
def update_chart(countries, years):
    # Convert selected years to integers because they were strings
    years = [int(year) for year in years]
    
    # Filter DataFrame based on selected years
    filtered_df = countryPerCap_sorted[(countryPerCap_sorted['year'].astype(int) >= years[0]) & (countryPerCap_sorted['year'].astype(int) <= years[1])]
    
    # Filter DataFrame based on selected countries if any are selected
    if countries:
        filtered_df = filtered_df[filtered_df['country'].isin(countries)]
    
    # Create list of year/lines/gdpPerCap based on filtered df
    lines = []
    if not filtered_df.empty:
        for country in filtered_df['country'].unique():
            country_data = filtered_df[filtered_df['country'] == country]
            line = dict(
                x=country_data['year'],
                y=country_data['gdpPercap'],
                mode='lines',
                name=country
            )
            lines.append(line)

    # Return updated figure
        return {
            'data': lines,
            'layout': dict(
                title='GDP per Capita by Country Through the Years',
                xaxis={'title': 'Year'},
                yaxis={'title': 'GDP per Capita'}
            )
        }


if __name__ == '__main__':
    app.run_server(debug=True)


