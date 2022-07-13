import plotly.express as px
import requests
import json
import pandas as pd
import numpy as np


r = requests.get('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json')
counties = json.loads(r.text)
target_states = ['47']
counties['features'] = [f for f in counties['features'] if f['properties']['STATE'] in target_states]

# create dataframes
df = pd.read_csv('data/Copy-of-Zip-Code-Report-(11)-clean.csv', usecols=['CTYNAME', 'attendance'], dtype={'fips': str})
df2 = pd.read_csv('data/county-populations.csv', usecols=['CTYNAME', 'pop2022'])
df3 = pd.read_csv('data/county_fips.csv')

# merge df and df2
final_df = pd.merge(df, df2, on='CTYNAME')
# delete "County" from names in CTYNAME column
final_df['CTYNAME'] = final_df['CTYNAME'].str.replace(' County', '')
# merge to df3
final_df = pd.merge(final_df, df3, on='CTYNAME')
# find percentage (attendance from 1 county / total ACS attendance)
final_df['percent-attendance-total'] = ((final_df['attendance'] / final_df['attendance'].sum()) * 100)
# find percentage (attendance from 1 county / 1 county's population)
final_df['percent-attendance-cty'] = ((final_df['attendance'] / final_df['pop2022']) * 100)
# rename columns
final_df.rename(columns={'percent-attendance-total': 'percent_attendance_total', 'percent-attendance-cty': 'percent_attendance_cty'}, inplace=True)
# add new column that rounds up to whole number
final_df['percent_attendance_cty_rounded'] = final_df['percent_attendance_cty']
final_df['percent_attendance_cty_rounded'] = final_df['percent_attendance_cty_rounded'].apply(np.ceil)
# add another new column that rounds up to whole number
final_df['percent_attendance_total_rounded'] = final_df['percent_attendance_total']
final_df['percent_attendance_total_rounded'] = final_df['percent_attendance_total_rounded'].apply(np.ceil)

# create map
fig_total_percent = px.choropleth(data_frame=final_df,
                                  locations='fips',
                                  geojson=counties,
                                  color='percent_attendance_total',
                                  labels={'fips': 'County FIPS code', 'percent_attendance_total': 'Attendance from county as percent of total ASC attendance'},
                                  color_continuous_scale='Viridis',
                                  range_color=(0, 12),
                                  scope='world',
                                  )
fig_total_percent.update_geos(fitbounds="locations", visible=False)
fig_total_percent.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
fig_total_percent.show()

fig_cty_percent = px.choropleth(data_frame=final_df,
                                locations='fips',
                                geojson=counties,
                                color='percent_attendance_cty',
                                color_continuous_scale='Blues',
                                range_color=(0, 12),
                                scope='world'
                                )
fig_cty_percent.update_geos(fitbounds="locations", visible=False)
fig_cty_percent.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
fig_cty_percent.show()


# function for plot #3 (visitors as percent of county population)
def plot_discrete_map(column_color, color_list, legend_list, rename_label_1):
    map_name = px.choropleth(data_frame=final_df,
                             locations='fips',
                             geojson=counties,
                             color=column_color,
                             color_discrete_sequence=color_list,
                             category_orders={column_color: legend_list},
                             scope='world',
                             labels={column_color: rename_label_1, 'CTYNAME': 'County name'},
                             hover_data={'fips': False, 'CTYNAME': True}
                            )
    map_name.update_geos(fitbounds="locations", visible=False)
    map_name.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
    map_name.show()


# make plot #3 from above function
final_df['percent_attendance_cty_rounded'] = final_df['percent_attendance_cty_rounded'].astype(str)
plot_discrete_map(column_color='percent_attendance_cty_rounded', color_list=['#ffffff', '#e1e2ec', '#c4c6d9', '#a7aac6', '#8b90b3', '#6f76a1', '#525d8f', '#34467d', '#08306b'], legend_list=['0.0', '1.0', '2.0', '3.0', '4.0', '5.0', '6.0', '7.0', '8.0'], rename_label_1='Visitors as a percent of county population')

# visitors as percent of county population
final_df['percent_attendance_cty_rounded'] = final_df['percent_attendance_cty_rounded'].astype(str) # include in function?
fig_cty_percent_discrete = px.choropleth(data_frame=final_df,
                                         locations='fips',
                                         geojson=counties,
                                         color='percent_attendance_cty_rounded',
                                         color_discrete_sequence=['#ffffff', '#e1e2ec', '#c4c6d9', '#a7aac6', '#8b90b3', '#6f76a1', '#525d8f', '#34467d', '#08306b'],
                                         # color_discrete_sequence=px.colors.qualitative.Dark2,
                                         category_orders={'percent_attendance_cty_rounded': ['0.0', '1.0', '2.0', '3.0', '4.0', '5.0', '6.0', '7.0', '8.0']},
                                         # range_color=(0, 12),
                                         scope='world',
                                         labels={'percent_attendance_cty_rounded': 'Visitors as a percent of county population', 'CTYNAME': 'County name'},
                                         hover_data={'fips': False, 'CTYNAME': True}
                                         )
fig_cty_percent_discrete.update_geos(fitbounds="locations", visible=False)
fig_cty_percent_discrete.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
fig_cty_percent_discrete.show()

# visitors as percent of total attendance
final_df['percent_attendance_total_rounded'] = final_df['percent_attendance_total_rounded'].astype(str)
fig_total_percent_discrete = px.choropleth(data_frame=final_df,
                                           locations='fips',
                                           geojson=counties,
                                           color='percent_attendance_total_rounded',
                                           color_discrete_sequence=['#f4f4f4', '#d4d4d4', '#b5b5b5', '#969696', '#797979', '#5d5d5d', '#424242', '#292929', '#121212'],
                                           # color_discrete_sequence=px.colors.qualitative.Dark2,
                                           category_orders={'percent_attendance_total_rounded': ['0.0', '1.0', '2.0', '3.0', '6.0', '7.0', '13.0', '47.0']},
                                           scope='world',
                                           labels={'percent_attendance_total_rounded': 'Visitors as a percent of total attendance', 'CTYNAME': 'County name'},
                                           hover_data={'fips': False, 'CTYNAME': True}
                                           )
fig_total_percent_discrete.update_geos(fitbounds="locations", visible=False)
fig_total_percent_discrete.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
fig_total_percent_discrete.show()

# raw attendance (plot #1)
fig_attendance = px.choropleth(
                                data_frame=final_df,
                                locations='fips',
                                geojson=counties,
                                color='attendance',
                                color_continuous_scale='Blues',
                                # range_color=(0, 25000),
                                # color_discrete_sequence=px.colors.qualitative.Dark2,
                                # category_orders={'attendance': ['0.0', '1.0', '2.0', '3.0', '6.0', '7.0', '13.0', '47.0']},
                                scope='world',
                                labels={'attendance': 'Raw attendance', 'CTYNAME': 'County name'},
                                hover_data={'fips': False, 'CTYNAME': True}
                                )
fig_attendance.update_geos(fitbounds="locations", visible=False)
fig_attendance.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
fig_attendance.show()
