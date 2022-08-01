import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime


def plot_indicators(_df):

    _df[['spx', 'gold', 'usoil']] = np.log(_df[['spx', 'gold', 'usoil']])
    fig = go.Figure()
    fig = make_subplots(rows=3, cols=1,shared_xaxes=True,
                    vertical_spacing=0.03, horizontal_spacing = 0.02, row_width=[0.2,0.2,0.6], 
                    specs=[ [{"secondary_y": True}], [{"secondary_y": False}] ,[{"secondary_y": False}] ], 
                    subplot_titles=(None, "Federal Funds Rate",  "CPI/PPI")
                    )
    fig.add_trace(go.Scatter(x=_df.date, y=_df['spx'], line_color='orange', name='S&P 500'), secondary_y=False, row=1, col=1)
    fig.add_trace(go.Scatter(x=_df.date, y=_df['gold'], line_color='gold', name='Gold'), secondary_y=False, row=1, col=1)
    fig.add_trace(go.Scatter(x=_df.date, y=_df['usoil'], line_color='black', name='usoil'), secondary_y=False, row=1, col=1)
    fig.add_trace(go.Scatter(x=_df.date, y=_df['yc'], line=dict(color='red', width=1), name='Yield Curve'), secondary_y=True,  row=1, col=1)
    fig.update_yaxes(title_text="Natural Log", secondary_y=False, row=1, col=1)
    fig.update_yaxes(title_text="Yield Curve %", secondary_y=True, row=1, col=1)

    # EFF
    fig.add_trace(go.Scatter(x=_df.date, y=_df["eff"],name="EFF", showlegend=False), row=2, col=1)
    fig.update_yaxes(title_text="Rate", row=2, col=1)

    # CPI/PPI
    fig.add_trace(go.Scatter(x=_df.date, y=_df["cpi"],name="CPI", fill='tozeroy'), row=3, col=1)
    fig.update_yaxes(title_text="YoY %", row=3, col=1)
    fig.add_trace(go.Scatter(x=_df.date, y=_df["ppi"],name="PPI", fill='tozeroy'), row=3, col=1)
    fig.update_yaxes(title_text="YoY %", row=4, col=1)

    # ISM, Sentiment, nonfarm
    _df["ism"] = _df["ism"] - 50
    #fig.add_trace(go.Bar(x=_df.date, y=_df["ism"],name="ISM", showlegend=False), row=4, col=1) 
    #fig.update_yaxes(title_text="Unit", row=3, col=1)
    
    # Recession Dates
    r_dates = [ ('1980-01', '1980-07'),
                ('1981-08', '1982-11'),
                ('1990-07', '1991-03'),
                ('2001-03', '2001-11'),
                ('2007-12', '2009-07'),
                ('2020-02', '2020-04'), ]

    for r in r_dates:
        if(r[0] in _df.date):
            fig.add_vrect(x0=r[0], x1=r[1], 
                fillcolor="#eeeee4", opacity=0.4, line_width=1,line_dash="dash", row=1, col=1)
            fig.add_vrect(x0=r[0], x1=r[1], 
                fillcolor="#eeeee4", opacity=0.4, line_width=1,line_dash="dash", row=2, col=1)
            fig.add_vrect(x0=r[0], x1=r[1], 
                fillcolor="#eeeee4", opacity=0.4, line_width=1,line_dash="dash", row=3, col=1)

        

    # Update Figure Properties
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            height=1000)
    
    return (fig)


def index_data(data):
    data = np.asarray(data)
    r = np.append(1, data[1:] / data[:-1])
    return r.cumprod() * 100

e_indicators = pd.read_csv("src/economic_indicators.csv", parse_dates=["DATE"], index_col='DATE')
e_indicators['cpi'] = e_indicators['cpi'].pct_change(12)
e_indicators['ppi'] = e_indicators['ppi'].pct_change(12)

r = list(range(1989, 2025,1))
mark = {i: {"label": str(i), "style": {"transform": "rotate(45deg)"}} for i in r}

# Dash web app
app = Dash(__name__)

# Configure UI 
app.layout = html.Div([
    html.Div([
        html.Pre(children= "United States Economic Indiactors",
        style={"text-align": "center", 'margin-bottom':0, 'font-family':'sans-serif', "font-size":"30px", "color":"black"}),
    ]),
    html.Div(
            [html.Pre(id='output-container-range-slider',
            style={"text-align": "center", 'font-family':'sans-serif', "font-size":"14px", "color":"black"}),
            dcc.RangeSlider(
                min=1989,
                max=2024,
                step=None,
                marks=mark,
                value=[1989, 2024],
                id='my-range-slider'
            )
    ], style={'margin': "auto", 'width':'800px', "text-align": "center"}),    
    html.Div([dcc.Graph(
        id='wealth',
    )], style={} ),

])
@app.callback(
    [ Output('output-container-range-slider', 'children'), Output('wealth', 'figure')],
    [Input('my-range-slider', 'value')])


def update_output(value):
    min_date = str(min(value))
    max_date = str(max(value))

    df = e_indicators[min_date:max_date].copy()
    df["date"] = df.index 

    # Plot Wealth
    fig = plot_indicators(df.copy())
    

    date_select = "(" + min_date +" - " + max_date +")"
    return date_select,  fig

if __name__ == '__main__':
    app.run_server(debug=True)

