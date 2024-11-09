import numpy as np
import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash import dcc, html, Input, Output, State
from dash import dash_table
from dash import Dash, dcc, html, dash_table, Input, Output, State, callback
from dash.dependencies import Input, Output, ALL
import plotly.express as px
import plotly.graph_objects as go
import warnings
import base64
import io
import statsmodels
from .functions import *
from scipy.optimize import curve_fit
import textwrap

#from flask import Flask
warnings.filterwarnings('ignore')


def create_dash_app(flask_app):

    # making a dash to run in the server __name__; stylesheet = html styling
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], server=flask_app, url_base_pathname='/dash/') # this mounts the Dash app at /dash/ ("/" by default is required at the end)

    # create a background template for plots
    templates = ['plotly', 'seaborn', 'simple_white', 'ggplot2',
                'plotly_white', 'plotly_dark', 'presentation', 'xgridoff',
                'ygridoff', 'gridon', 'none']


    # create a blank figure to prevent plotly dash error when runnng the app, even though it still works without this.
    def blankfigure():
        figure = go.Figure(go.Scatter(x=[],y=[]))
        figure.update_layout(template = None)
        figure.update_xaxes(showgrid = False, showticklabels = False, zeroline = False)
        figure.update_yaxes(showgrid = False, showticklabels = False, zeroline = False)

        return figure


    app.layout = html.Div([
    
        html.Div([
            # components for label and input content by user
            dbc.Row([dbc.Col(html.H1('Plotter App', style={'textAlign': 'center', "font-size":"60px"}))]), # title
            
            # first set the overall layout, where the figure will be side by side with the plot tools and filter options (details will be included in the subsequent callbacks)
            dbc.Row([
                dbc.Col([ # div container for the fig
                    dbc.Row([dbc.Col([html.Label('Upload file',style={'marginLeft': '50px',"font-size":"20px"})])]),
                    dbc.Row([
                            dbc.Col([dcc.Upload(id='upload-data',children=html.Div(['Drag and Drop or ',html.A('Select Files')]),
                            style={
                                'width': '100%',
                                'height': '60px',
                                'lineHeight': '60px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin': '5px 0px 0px 0px'
                                }, multiple=False)], width=3,lg=6, xs=6), # Allow multiple files to be uploaded is false. lg=6 and xs=6 (or any other values that add up to 12) to ensure that elements maintain a side-by-side layout regardless of the screen size
                            dbc.Col([dcc.RadioItems(id = 'show_hide_table_button', options = ['show_table', 'hide_table','show_plot'], value = 'hide_table')], width=2,lg=6, xs=6)
                            ]), 
                    html.Div(id='output-data-upload', children=''),
                    html.Div(id='colorby1'),
                ], width=8, style={'marginLeft': '25px'}), # width is the overall width of the components above, the witdth of all dbc.col (within the same row) can be max of 12
                
                dbc.Col([ # div container for the plot tools
                    # dcc.RadioItems(id = 'show_hide_plot_tools_button', options = ['plot_tools','hide_plot_tools'], value = 'plot_tools', inline=True),
                    html.Div(id='plot_tools', children=''),
                    html.Div(id='data_for_plot1', children=''),             
                    # for output error message
                    html.Div(id='error_message', style={'color': 'red', 'font-size': '20px', 'text-align': 'center', 'display': 'flex'})
                ], width=3, style={'marginLeft': '25px'},lg=3, xs=3),
            ], className='container-fluid'),

            dbc.Row([
                html.Div(id='downloadable_data', children=''),
            ])    
        ], style={'border': '2px solid black', 'padding': '10px', 'borderRadius': '5px', 'margin': '25px'}),
    ])

    def parse_contents(contents, file_name): # 'contents/filename' property is needed for callbacks
        
        content_type, content_string = contents.split(',')
        #print(content_type)
        
        decoded = base64.b64decode(content_string)
        #print(decoded)
    
        if 'csv' in file_name:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in file_name:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        elif 'txt' in file_name:
            # Assume that the user uploaded an text file
            # 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte -> USE utf-16
            df = pd.read_csv(io.StringIO(decoded.decode('utf-16')), delimiter = '\t') # \t separates columns separated by tabs

        return df

    @app.callback(
        Output('output-data-upload', 'children'),
        Output('plot_tools', 'children'),
        [Input('upload-data', 'contents'), # refer to first arg in upload_data_file()
        Input('upload-data', 'filename'), # refer to 2nd arg in upload_data_file()
        Input(component_id = 'show_hide_table_button', component_property = 'value')] # refer to 3rd arg in upload_data_file()
        
        #State('upload-data', 'last_modified'),
        #prevent_initial_call=True
    )
        
    def upload_data_file(contents, file_name, display):
        show_table = html.Div()
        app.show_plot = html.Div() # similar to app.layout

        if contents is not None:
            uploaded_df = parse_contents(contents, file_name) # dataframe object
            dropdown = uploaded_df.columns
            show_table = html.Div([
                        dbc.Row([dbc.Col([html.H5(file_name)])]),
                        
                        # show data table
                        dbc.Row([dbc.Col([dash_table.DataTable(data=uploaded_df.to_dict('records'), columns=[{"name": i, "id": i} for i in uploaded_df.columns])])]),
                        ])

            app.show_plot = html.Div([
                        dbc.Row([dbc.Col([html.H5(file_name)])]),
                        # component for show dropdown options
                        dbc.Row([dbc.Col(html.Label('Select x-axis from dropdown'), lg=3, xs=3), #width = between Cols
                                dbc.Col(dcc.Dropdown(id = 'xaxis_column1', options = dropdown, value = None),lg=4, xs=4),
                                # dbc.Col(html.Label('Select x-axis from dropdown'), width=2), #width = between Cols
                                # dbc.Col(dcc.Dropdown(id = 'xaxis_column2', options = dropdown, value = None)),
                                ]),

                        dbc.Row([dbc.Col(html.Label('Select y-axis from dropdown'), lg=3, xs=3),
                                dbc.Col(dcc.Dropdown(id = 'yaxis_column1', options = dropdown, value = None, multi = True),lg=6, xs=6),
                                # dbc.Col(html.Label('Select y-axis from dropdown'), width=2),
                                # dbc.Col(dcc.Dropdown(id = 'yaxis_column2', options = dropdown, value = None, multi = True)),
                                ]),

                        dbc.Row([dbc.Col(html.Label('Select group column from dropdown'), lg=3, xs=3),
                                dbc.Col(dcc.Dropdown(id = 'groupby1', options = dropdown, value = None, multi = True),lg=6, xs=6),
                                # dbc.Col(html.Label('Select group column from dropdown'), width=2),
                                # dbc.Col(dcc.Dropdown(id = 'groupby2', options = dropdown, value = None, multi = False)),
                                ]),
                        
                        # html.Div(id='data_for_plot1', children=''),
                        # html.Div(id='data_for_plot2', children=''),
                        
                        # In the subsequent callback, use this to store the variable 'groupby' values for dropdown (used as output)
                        dcc.Store(id='stored_groupby1'),

                        # div container for colorby dropdown which will contain the colorby dropdown menu
                        html.Div(id='colorby_container', children=''),
                        
                        # store the dataframe for use in subsequent callbacks
                        dcc.Store(id = 'stored_data', data = uploaded_df.to_dict('records')),
                        
                        html.Br(),
            
                        # components for graph, initially blank
                        dbc.Row([dbc.Col(dcc.Graph(id="graph1", figure=blankfigure())),
                                ]), 

                        # for storing data container that will be used for downloading
                        html.Div(id = 'download_data_container'),
                        dcc.Store(id='download_data')
                        ])
        
            app.plot_tools = html.Div([
                dbc.Row([html.Label('Plot tools',style={"font-size": "30px",'text-align':'center','margin':'0px 0px 10px 0px'}),
                        ]),

                dbc.Row([dbc.Col(html.Label('Select Background Style',style={"font-size": "15px"}))]),
                dbc.Row([dbc.Col(dcc.RadioItems(id='template1', options = [{'label': k, 'value': k} for k in templates], value = None, inline=True)),
                        ]), # grid style

                html.Br(),

                dbc.Row([dbc.Col(html.Label('Select Plot Type',style={"font-size": "15px"}), width=4),
                        dbc.Col(dcc.Dropdown(id = 'plot_type1', options = ['scatter','line','bar','box'], value = 'line', style={'font-size':15}), width=8),
                        ]),
                
                html.Br(),

            
                dbc.Row([dbc.Col(html.Label('Select Trendline (scatter only)',style={"font-size": "15px"}),lg=4, xs=4), # lg/xs can control the width
                        dbc.Col(dcc.Dropdown(id = 'trendline', options = ['linear','exponential1','exponential2','polynomial'], value = 'line', style={'font-size':15}),lg=5, xs=5),
                        dbc.Col(html.Div(id='polynomial_value_for_trendline',children=''), width=5),
                        ]),


                html.Br(),  
                dbc.Row([dbc.Col(html.Label('Select Interpolation Method',style={"font-size": "15px"}),width=6),
                        dbc.Col(dcc.Dropdown(id = 'interpolation_method', options = ['linear', 'pad', 'polynomial', 'piecewise_polynomial'], value = None, style={'font-size':15}, multi = False),width=6)
                        ]),

                html.Br(),
                dbc.Row([dbc.Col(html.Label('Select Interpolation Direction',style={"font-size": "15px"}),width=6),
                        dbc.Col(dcc.Dropdown(id = 'interpolation_limit_direction', options = ['forward', 'backward', 'both'], value = None, style={'font-size':15}, multi = False),width=6)
                        ]),

                html.Br(),
                dbc.Row([dbc.Col(html.Label('Select Poly-order For Interpolation',style={"font-size": "15px"}),width=8),
                        dbc.Col(dcc.Input(id='poly order', type='number', min=0, max=10, step=1,style={'font-size':15}),width=3)
                        ]),
            ])
            
        # connecting radio button options with output of upload button
        if display == 'show_table': 
            return show_table, ''
        if display == 'hide_table':
            return None, None
        if display == 'show_plot':
            return app.show_plot, app.plot_tools


    @app.callback( 
        Output(component_id='polynomial_value_for_trendline', component_property='children'),
        Input(component_id='trendline', component_property='value'),
    )

    def polynomial_value_for_trendline(trendline):

        if trendline == 'polynomial':
            polydegree = html.Div(
                    dbc.Row([dbc.Col(html.Label('Enter degree',style={"font-size": "15px"}),lg=3, xs=3),
                            dbc.Col(dcc.Input(id='poly degree', type='number', min=0, max=10, style={'font-size':15,'width':'50%'}))
                            ]),
                )
            return polydegree

        else:
            polydegree = html.Div(
                    dcc.Input(id='poly degree', type='number', min=0, max=10, style={'display':'none'}),
                )
            return polydegree


    # call back getting unique values for group, and show the filter list options of the unique values
    @app.callback( 
        Output(component_id='data_for_plot1', component_property='children'),
        Output('stored_groupby1', 'data'), # store the groupby values for dropdown as output in the return
        Input(component_id='groupby1', component_property='value'),
        State('stored_data', 'data'),
    )

    def data_for_plot1(groupby1, stored_data):

        # # print(stored_data)
        uploaded_df = pd.DataFrame(stored_data)

        filter_dropdowns = []

        # adding title first
        filter_dropdowns.append(dbc.Row([html.Label('Filter Options',style={'text-align':'center','font-size':20,'margin':'50px 0px 10px 0px'})]))

        # dropdown populates as group values are selected
        for group in groupby1:
            unique_values = uploaded_df[group].unique()
            filter_dropdowns.append(
                html.Div([
                    dbc.Row([dbc.Col([html.Label(group)])]),
                    dbc.Row([dbc.Col([dcc.Dropdown(id={"type": "filter-dropdown", "index": group}, options=unique_values, value=None,multi=True,persistence=True,persistence_type="memory") # persistence allows dropdown and selected values to be kept in memory
                        ])
                    ])
                ])
            )

        return filter_dropdowns, groupby1

    # callback for colorby dropdown using the stored groupby variable from the previous callback
    @app.callback(
        Output('colorby_container', 'children'),
        Input('stored_groupby1', 'data'),
    )
    def update_colorby_dropdown(groupby1):
        
        colorby_dropdown = html.Div([
            dbc.Row([
                dbc.Col(html.Label('Colorby'), width=2),
                dbc.Col(dcc.Dropdown(id='colorby1',options=groupby1,value=None,multi=False,persistence=True,persistence_type="memory"), width=4)
            ])
        ])

        return colorby_dropdown


    # Callback to read values from multiple filter-dropdown and use them to filter the dataframe, and store in selected-filter-values-store.
    # using the dependencies "ALL" to read all the values from the multiple filter-dropdown
    @app.callback(
        Output(component_id='graph1', component_property='figure'),
        Output(component_id='error_message', component_property='children'),
        #Output(component_id='download_data_container', component_property='children'),
        Output(component_id='download_data', component_property='data'),
        Input(component_id='xaxis_column1', component_property='value'),
        Input(component_id='yaxis_column1', component_property='value'),
        Input(component_id='stored_data', component_property='data'),
        Input({'type': 'filter-dropdown', 'index': ALL}, 'value'),
        Input(component_id='groupby1', component_property='value'),
        Input(component_id='colorby1', component_property='value'),
        Input(component_id='template1', component_property='value'),
        Input(component_id = 'plot_type1', component_property = 'value'),
        Input(component_id = 'trendline', component_property = 'value'),
        Input(component_id='interpolation_method', component_property='value'),
        Input(component_id='interpolation_limit_direction', component_property='value'),
        Input(component_id='poly order', component_property='value'),
        Input(component_id='poly degree', component_property='value'),
    )

    def update_selected_filter_values(xaxis, yaxis, stored_data, selected_values, group, colorby,template, plot_type,trendline,interpolation_method,interpolation_limit_direction,poly_order,degree):
        
        # ctx = dash.callback_context # shows which input triggered the callback
        # triggered_input = ctx.triggered[0]['prop_id'].split('.')[0]
        # print(triggered_input)
        
        error_message = ''

        uploaded_df = pd.DataFrame(stored_data)

        df1 = uploaded_df.where(pd.notnull(uploaded_df), None)
        if interpolation_method and interpolation_limit_direction:
            df1 = uploaded_df.interpolate(method=interpolation_method, order=poly_order, limit_direction=interpolation_limit_direction, axis=0)
        
        df = df1.copy()

        if len(df.index) == 0:
            df = None

        fig = go.Figure()

        # create list of yaxis string for multiple yaxis plots 
        yaxis_num = []
        for count in range(len(yaxis)):
            count += 1
            string = 'y'+ str(count)
            yaxis_num.append(string)

        if xaxis and yaxis:
            if group:
                if selected_values:
                    # filter the dataframe based on the selected filter columns and filter values
                    selected_dict = dict(zip(group, selected_values))
                    for col_name, values in selected_dict.items():
                        if values is not None:
                            if len(values) > 0:
                                df = df[df[col_name].isin(values)]
                
                # append xaxis and group to a list for grouping
                group.append(xaxis)
                groupbylist = list(set(group)) # remove duplicates
                grouped_df = df.groupby(groupbylist).mean(numeric_only=True).reset_index()
                grouped_std = df.groupby(groupbylist).std(numeric_only=True).reset_index() # without unstack, the standard deviation works with multiple filter options

            else:
                grouped_df = df.groupby([xaxis]).mean(numeric_only=True).reset_index()
                grouped_std = df.groupby([xaxis]).std(numeric_only=True).reset_index()
            
            #grouped_df_copy = grouped_df.copy().to_dict('records')

            if plot_type == 'bar':  
                # create plots 
                if len(yaxis) < 2:
                    if len(yaxis) == 1 and yaxis[0] == xaxis:
                        yaxis = yaxis[0]
                    yerror = grouped_std[yaxis].values.tolist()
                    # print('yerror array with single yaxis is',yerror)
                    fig = px.bar(grouped_df, x=xaxis, y=yaxis, color=colorby, barmode='group',error_y=yerror) # histfunc='avg', text_auto = True, title = '{} vs {}'.format(xaxis, yaxis))
                    key_name = 'yaxis'
                    yaxis_arg = dict(title=yaxis[0])
                    labels = {key_name: yaxis_arg}
                    fig.update_layout(labels)
                else:
                    if group or selected_values:
                        for value in selected_values:
                            for i,yaxis_name in enumerate(yaxis):
                                yerror = grouped_std[yaxis_name].values.tolist()
                                # print('yerror array with multiple yaxis is',yerror)
                                fig.add_trace(go.Bar(name = f'{yaxis_name} {value}', x=grouped_df[xaxis], y=grouped_df[yaxis_name], textposition='auto',error_y={'type':'data', 'array':yerror}))
                    else:
                        for i, yaxis_name in enumerate(yaxis):
                            yerror = grouped_std[yaxis_name].values.tolist()
                            fig.add_trace(go.Bar(name = yaxis_name, x=grouped_df[xaxis], y=grouped_df[yaxis_name], textposition='auto',error_y={'type':'data', 'array':yerror}))
                
                
                yerror_copy = grouped_std[yaxis].rename(columns={','.join(yaxis):','.join(yaxis) + '_std'})
                yaxis.insert(0, xaxis)
                grouped_df_copy = grouped_df[yaxis].copy()
                downloadable_df = pd.concat([grouped_df_copy, yerror_copy], axis=1).to_dict('records')
        
                fig.for_each_trace(lambda trace: trace.update(name='<br>'.join(textwrap.wrap(trace.name, width=15)))) # wrap the trace name
                fig.update_layout(barmode='group')
                fig.update_layout(template=template)

            
            if plot_type == 'line':
                # create plots 
                if len(yaxis) < 2:
                    if len(yaxis) == 1 and yaxis[0] == xaxis:
                        yaxis = yaxis[0]
                    yerror = grouped_std[yaxis].values.tolist()
                    fig = px.line(grouped_df, x=xaxis, y=yaxis, title = '{} vs {}'.format(xaxis, yaxis), markers=True, color=colorby, error_y=yerror)
                else:
                    if group or selected_values:
                        for value in np.array(selected_values).flatten().tolist():
                            # print('filtered_df is',filtered_df)
                            for i, yaxis_name in enumerate(yaxis):
                                yerror = grouped_std[yaxis_name].values.tolist()
                                x_data = grouped_df[grouped_df[colorby].isin([value])][xaxis]
                                y_data = grouped_df[grouped_df[colorby].isin([value])][yaxis_name]
                                fig.add_trace(go.Scatter(name = f'{yaxis_name} {value}', x=x_data, y=y_data, mode='lines+markers', yaxis = yaxis_num[i], error_y={'type':'data', 'array':yerror})) #marker_color='#d99b16',hoverinfo='none'))

                    else:
                        for i, yaxis_name in enumerate(yaxis):
                            yerror = grouped_std[yaxis_name].values.tolist()
                            #print(xaxis_column, yaxis_column)
                            fig.add_trace(go.Scatter(name = yaxis_name, x=grouped_df[xaxis], y=grouped_df[yaxis_name], mode='lines+markers', yaxis = yaxis_num[i],error_y={'type':'data', 'array':yerror})) #marker_color='#d99b16',hoverinfo='none'))

                # if plotting against the same column, yerror will give error cuz there is no std. deal with this using try/except
                try:
                    yerror_copy = grouped_std[yaxis].rename(columns={','.join(yaxis):','.join(yaxis) + '_std'})
                    yaxis.insert(0, xaxis)
                except:
                    yerror_copy = None
                    yaxis = yaxis
                
                grouped_df_copy = grouped_df[yaxis].copy()
                downloadable_df = pd.concat([grouped_df_copy, yerror_copy], axis=1).to_dict('records')
                
                # set a another variable for the appropriate indices in yaxis 
                yaxis_labels = yaxis[1:]

                # create a dictionary for yaxis for multiple yaxis
                args_for_update_layout = dict()
                for i, yaxis_name in enumerate(yaxis_labels):
                    key_name = 'yaxis' if i ==0 else f'yaxis{i+1}'
                    if i == 0:
                        yaxis_args = dict(title=yaxis_labels[0])
                    else:
                        yaxis_args = dict(title=yaxis_name, anchor = 'free', overlaying =  'y', side = 'left', autoshift = True)
                    
                    # populate the dictionary
                    args_for_update_layout[key_name] = yaxis_args
                    #print(args_for_update_layout)

                #fig.for_each_trace(lambda trace: trace.update(name='<br>'.join(textwrap.wrap(trace.name, width=15)))) # wrap the trace name
                # update layout using yaxis dictionary.
                fig.update_layout(**args_for_update_layout)
                fig.update_layout(template=template)


            if plot_type == 'scatter':
                # create plots 
                if len(yaxis) < 2:
                    if len(yaxis) == 1 and yaxis[0] == xaxis:
                        yaxis = yaxis[0]
                    yerror = grouped_std[yaxis].values.tolist()
                    fig = px.scatter(grouped_df, x=xaxis, y=yaxis, title = '{} vs {}'.format(xaxis, yaxis), color=colorby,error_y=yerror)
                    
                    # Extract colors used by px.scatter so the fit lines can have the same color
                    colors = [trace.marker.color for trace in fig.data if trace.mode == 'markers']

                    # problem: trace name should be same as figure name
                    if trendline and colorby:
                        unique_group = grouped_df[colorby].unique() 
                        for i, unique in enumerate(unique_group):
                            filtered_df = grouped_df[grouped_df[colorby] == unique] # filter the data by colorby in order to fit trendline to individual and all lines
                            try:
                                # sigma_yerror = grouped_std[yaxis].replace(np.nan, 0).to_numpy().flatten()
                                # mean_sigma = np.mean(sigma_yerror[np.nonzero(sigma_yerror)])
                                # sigma_yerror[sigma_yerror == 0] = mean_sigma
                                x = filtered_df[xaxis].to_numpy().flatten() # convert 2D array to 1D
                                y = filtered_df[yaxis].to_numpy().flatten()
                                if trendline == 'linear':
                                    reg, cov  = curve_fit(LinearRegression, x, y) #sigma is the one that will make regression fit through error bars
                                    yfit=LinearRegression(x, *reg)              
                                if trendline == 'exponential':
                                    reg, cov  = curve_fit(ExponentialRegression, x, y)
                                    yfit=ExponentialRegression(x, *reg)
                                if trendline == 'exponential2':
                                    reg, cov  = curve_fit(ExponentialRegression2, x, y)
                                    yfit=ExponentialRegression2(x, *reg)
                                if trendline == 'polynomial':
                                    reg, yfit = PolynomialRegression(x,y,degree)
                            
                                rmse = np.sqrt(np.mean((yfit - y)**2))
                                formatted_reg = [f'{coef:.2f}' for coef in reg]
                                text = 'coef = {}, RMSE ={:.2f}'.format(formatted_reg,rmse)
                                fig.add_trace(go.Scatter(name = f'{unique}, {text}', x=x, y=yfit, mode='lines', line=dict(dash='dash',color=colors[i])))
                            except Exception as e:
                                error_message = f"Cannot fit trendline. Scatter plot only. May be missing data or try another fit method: {e}"
                                return fig, error_message, downloadable_df
                    if trendline and not colorby:
                        try:
                            # sigma_yerror = grouped_std[yaxis].replace(np.nan, 0).to_numpy().flatten()
                            # mean_sigma = np.mean(sigma_yerror[np.nonzero(sigma_yerror)])
                            # sigma_yerror[sigma_yerror == 0] = mean_sigma
                            x = grouped_df[xaxis].to_numpy().flatten() # convert 2D array to 1D
                            y = grouped_df[yaxis].to_numpy().flatten()
                            if trendline == 'linear':
                                reg, cov  = curve_fit(LinearRegression, x, y) #sigma is the one that will make regression fit through error bars
                                yfit=LinearRegression(x, *reg)              
                            if trendline == 'exponential':
                                reg, cov  = curve_fit(ExponentialRegression, x, y)
                                yfit=ExponentialRegression(x, *reg)
                            if trendline == 'exponential2':
                                reg, cov  = curve_fit(ExponentialRegression2, x, y)
                                yfit=ExponentialRegression2(x, *reg)
                            if trendline == 'polynomial':
                                reg, yfit = PolynomialRegression(x,y,degree)
                                print(reg)

                            rmse = np.sqrt(np.mean((yfit - y)**2))

                            formatted_reg = [f'{coef:.2f}' for coef in reg]
                            text = 'coef = {}, RMSE ={:.2f}'.format(formatted_reg,rmse)
                            fig.add_trace(go.Scatter(name = f'{yaxis}, {text}', x=x, y=yfit, mode='lines', line=dict(dash='dash')))
                        except Exception as e:
                            error_message = f"Cannot fit trendline. Scatter plot only. May be missing data or try another fit method: {e}"
                            return fig, error_message, downloadable_df
                            
                else:
                    if group or selected_values:
                        for value in np.array(selected_values).flatten().tolist():
                            for i, yaxis_name in enumerate(yaxis):
                                yerror = grouped_std[yaxis_name].values.tolist()
                                x_data = grouped_df[grouped_df[colorby].isin([value])][xaxis]
                                y_data = grouped_df[grouped_df[colorby].isin([value])][yaxis_name]
                                fig.add_trace(go.Scatter(name = f'{yaxis_name} + {value}', x=x_data, y=y_data, mode='markers', yaxis = yaxis_num[i], error_y={'type':'data', 'array':yerror})) #marker_color='#d99b16',hoverinfo='none'))
                            
                    else:
                        for i, yaxis_name in enumerate(yaxis):
                            yerror = grouped_std[yaxis_name].values.tolist()
                            #print(xaxis_column, yaxis_column)
                            fig.add_trace(go.Scatter(name = yaxis_name, x=grouped_df[xaxis], y=grouped_df[yaxis_name], mode='markers', yaxis = yaxis_num[i],error_y={'type':'data', 'array':yerror})) #marker_color='#d99b16',hoverinfo='none'))

                # if plotting against the same column, yerror will give error cuz there is no std. deal with this using try/except
                try:
                    yerror_copy = grouped_std[yaxis].rename(columns={','.join(yaxis):','.join(yaxis) + '_std'})
                    yaxis.insert(0, xaxis)
                except:
                    yerror_copy = None
                    yaxis = yaxis
                
                grouped_df_copy = grouped_df[yaxis].copy()
                downloadable_df = pd.concat([grouped_df_copy, yerror_copy], axis=1).to_dict('records')   

                # create a dictionary containing multiple dictionares of yaxis
                yaxis_labels = yaxis[1:]

                # create a dictionary for yaxis for multiple yaxis
                args_for_update_layout = dict()
                for i, yaxis_name in enumerate(yaxis_labels):
                    key_name = 'yaxis' if i ==0 else f'yaxis{i+1}'
                    if i == 0:
                        yaxis_args = dict(title=yaxis_labels[0])
                    else:
                        yaxis_args = dict(title=yaxis_name, anchor = 'free', overlaying =  'y', side = 'left', autoshift = True)
                    
                    # populate the dictionary
                    args_for_update_layout[key_name] = yaxis_args
                    #print(args_for_update_layout)
                    
                # update traces
                fig.for_each_trace(lambda trace: trace.update(name='<br>'.join(textwrap.wrap(trace.name, width=20)))) # wrap the trace name
                fig.update_layout(**args_for_update_layout) # update layout using yaxis dictionary for multiple yaxis
                fig.update_layout(template=template) # update graph background

            # maybe add a groupby so people can select a range of value
            if plot_type == 'box':
                # create plots 
                if len(yaxis) < 2:
                    if len(yaxis) == 1 and yaxis[0] == xaxis:
                        yaxis = yaxis[0]
                    # print('yerror array with single yaxis is',yerror)
                    fig = px.box(df, x=xaxis, y=yaxis, color=xaxis)
                    key_name = 'yaxis'
                    yaxis_arg = dict(title=yaxis[0])
                    labels = {key_name: yaxis_arg}
                    fig.update_layout(labels)
                else:
                    for i,yaxis_name in enumerate(yaxis):
                        # print('yerror array with multiple yaxis is',yerror)
                        fig.add_trace(go.Box(name = yaxis_name, x=df[xaxis], y=df[yaxis_name]))
                
                yaxis.insert(0, xaxis)
                downloadable_df = df[yaxis].copy().to_dict('records')
                fig.for_each_trace(lambda trace: trace.update(name='<br>'.join(textwrap.wrap(trace.name, width=15)))) # wrap the trace name
                fig.update_layout(barmode='group')
                fig.update_layout(template=template)


        else:
            return blankfigure(), error_message, None
    
        return fig, error_message, downloadable_df

    @callback(
        Output("downloadable_data", 'children'),
        Input("download_data", "data"),
        prevent_initial_call=True,
    )
    def download_data_button(data):
        
        if len(data) == 0 or data is None:
            return html.Div()

        else:
            download_button = html.Div([
                dcc.Input(id="filename", placeholder='Enter file name'),
                html.Button('Download Plot Data', id="btn_csv"),
                dcc.Download(id="download-dataframe-csv"), 
                ])

            return download_button
        
    @callback(
        Output("download-dataframe-csv", "data"),
        Output('filename', 'value'),
        Input("btn_csv", "n_clicks"),
        State("download_data", "data"), # state does not trigger the callback. It is used to pass the current value of a component to the callback function
        State("filename", "value"), # so "state" ensures download button is triggered when clicked. Typing in the filename doesnt trigger the callback
        prevent_initial_call=True, # Ensures this callback is not triggered on initial load
    )
    def dataframe_download(n_clicks,df,filename):
        # convert dictionary to dataframe
        data_for_download = pd.DataFrame(df)
        return dcc.send_data_frame(data_for_download.to_csv,f"{filename}.csv"), ''

    return app
    
if __name__ == "__main__":
    app = create_dash_app()
    app.run_server(debug=True) # or whatever you choose
    # app.run_server(debug=False,host="0.0.0.0", port=10000) #if deploying
    # kill port https://stackoverflow.com/questions/73309491/port-xxxx-is-in-use-by-another-program-either-identify-and-stop-that-program-o
    # turning global variables into dcc.Store https://stackoverflow.com/questions/75215360/pass-pandas-dataframe-between-functions-using-upload-component-in-plotly-dash
    # introduce different fits using scipy https://plotly.com/python/v3/exponential-fits/

    # for render, make sure requirements.txt has gunicorn. Also the main file is called main.py

    # problem - when selecting multiple yaxis, and group by specifc value like volume, and colorby volume, it doesnt separate out the trends based on volumes, rather it
    # will lump the volume values together a trend, for example it wll split the trends and each trend will contain all the filtered volume values. 
    # what I need is for the trend to split up based on the colorby value. This works when single y axis is chosen

