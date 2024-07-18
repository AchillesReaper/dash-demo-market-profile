from datetime import datetime
from dateutil.relativedelta import relativedelta
from dash import Dash, html, dcc, Output, Input
import plotly.graph_objects as go
import pandas as pd
import ast

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)

mp_file_path = 'https://raw.githubusercontent.com/AchillesReaper/dash-demo-market-profile/main/mp_HSI_2022-07_2024-06_rolling4.csv'
mp_df = pd.read_csv(mp_file_path, index_col=0)

mp_df_dict = mp_df.to_dict()

tpo_dict = {}
for key in mp_df_dict['tpo_count']:
    tpo_dict[key] = ast.literal_eval(mp_df_dict['tpo_count'][key])

fig = go.Figure()
cum_base = 0
pre_date = None

fig.update_layout(
    yaxis=dict(tickformat=','),
    xaxis=dict(showticklabels=False),
    autosize=True,
    xaxis_rangeslider_visible=True,
    height=1000,
)

app = Dash(__name__)
server = app.server
app.layout = [
    html.Div(
        className='row', 
        children='HSI Market Profile',
        style={'textAlign': 'center', 'fontSize': 30, 'fontfamily': 'Arial', 'margin': 'auto', 'padding': '10px'}
    ),
    html.Div(
        className='row', 
        children=dcc.DatePickerRange(
            id='user-pick-date-range',
            min_date_allowed=datetime.strptime(mp_df.index[0], "%Y-%m-%d").date() + relativedelta(days=1),
            max_date_allowed=datetime.strptime(mp_df.index[-1], "%Y-%m-%d").date(),
            start_date=datetime.strptime(mp_df.index[-1], "%Y-%m-%d").date() - relativedelta(months=1),
            end_date=datetime.strptime(mp_df.index[-1], "%Y-%m-%d").date(),
            display_format='D MMM YYYY',
            month_format='MMMM YYYY',
        ),
        style={'textAlign': 'center', 'width': '600px', 'margin': 'auto', 'padding': '10px'}
    ),
    # html.Div(
    #     className='row', 
    #     children=dcc.Graph(figure={}, id='market-profile-chart')
    # ),
    dcc.Graph(figure=fig, id='market-profile-chart')
]

@app.callback(
    Output(component_id='market-profile-chart', component_property='figure'),
    Input(component_id='user-pick-date-range', component_property='start_date'),
    Input(component_id='user-pick-date-range', component_property='end_date')
)
def update_output(start_date, end_date):
    fig.data = []
    start_date_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_date = datetime.strptime(end_date, "%Y-%m-%d")
    cum_base = 0
    pre_date = None
    for key in tpo_dict:
        if datetime.strptime(key, "%Y-%m-%d") < start_date_date or datetime.strptime(key, "%Y-%m-%d") > end_date_date:
            continue
        if pre_date is not None and mp_df.at[key, 'open'] >= mp_df.at[pre_date, 'close']:
                bar_color = 'blue'
        else:
            bar_color = 'red'

        fig.add_trace(go.Bar(
            name=key,
            x=[count for count in tpo_dict[key].values()],
            y=[price for price in tpo_dict[key].keys()],
            width=6,
            orientation='h',
            base=cum_base,
            opacity=1,
            marker=dict(color=bar_color)
            ))
        if len(tpo_dict[key]) > 0:
            cum_base += max(tpo_dict[key].values())
        pre_date = key
    
    return fig

app.run(debug=True, host='0.0.0.0', port=8050)
