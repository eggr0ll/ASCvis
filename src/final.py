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
memp_df = pd.read_csv('data/mosh_memphis.csv')
chatt_df = pd.read_csv('data/cdm_chattanooga.csv')
knox_df = pd.read_csv('data/muse_knox.csv')
john_df = pd.read_csv('data/hodc_john.csv')
murf_df = pd.read_csv('data/dcms_murf.csv')
combined_total_df = pd.read_csv('data/all_centers_data.csv')


# clean up dfs
# clean up ASC/Nashville
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

# clean up MoSH/Memphis df
# replace "nan" attendance values with 0
memp_df['attendance'] = memp_df['attendance'].fillna(0)
# find percentage (attendance from 1 county / 1 county's population)
memp_df['percent_attendance_cty'] = ((memp_df['attendance'] / memp_df['pop2022']) * 100)
# add new column that rounds up to whole number
memp_df['percent_attendance_cty_rounded'] = memp_df['percent_attendance_cty']
memp_df['percent_attendance_cty_rounded'] = memp_df['percent_attendance_cty_rounded'].apply(np.ceil)
# convert percent_attendance_cty_rounded from int type to str type to use discrete colors
memp_df['percent_attendance_cty_rounded'] = memp_df['percent_attendance_cty_rounded'].astype(str)

# clean up CDM/Chattanooga df
# delete "County" from names in CTYNAME column
chatt_df['CTYNAME'] = chatt_df['CTYNAME'].str.replace(' County', '')
# find percentage (attendance from 1 county / 1 county's population)
chatt_df['percent_attendance_cty'] = ((chatt_df['attendance'] / chatt_df['pop2022']) * 100)
# add new column that rounds up to whole number
chatt_df['percent_attendance_cty_rounded'] = chatt_df['percent_attendance_cty']
chatt_df['percent_attendance_cty_rounded'] = chatt_df['percent_attendance_cty_rounded'].apply(np.ceil)
# convert percent_attendance_cty_rounded from int type to str type to use discrete colors
chatt_df['percent_attendance_cty_rounded'] = chatt_df['percent_attendance_cty_rounded'].astype(str)

# consolidate and clean up Knoxville, Johnson City, and Murfreesboro centers
sites = ['knox', 'john', 'murf']
for site in sites:
    df_name = site + '_df'
    df = eval(df_name)
    df['attendance'] = df['attendance'].fillna(0)
    # delete "County" from names in CTYNAME column
    df['CTYNAME'] = df['CTYNAME'].str.replace(' County', '')
    # find percentage (attendance from 1 county / 1 county's population)
    df['percent_attendance_cty'] = ((df['attendance'] / df['pop2022']) * 100)
    # add new column that rounds up to whole number
    df['percent_attendance_cty_rounded'] = df['percent_attendance_cty']
    df['percent_attendance_cty_rounded'] = df['percent_attendance_cty_rounded'].apply(np.ceil)
    # convert percent_attendance_cty_rounded from int type to str type to use discrete colors
    df['percent_attendance_cty_rounded'] = df['percent_attendance_cty_rounded'].astype(str)

# clean up combined centers data
# delete "County" from names in CTYNAME column
combined_total_df['CTYNAME'] = combined_total_df['CTYNAME'].str.replace(' County', '')
# find percentage (attendance from 1 county / 1 county's population)
combined_total_df['percent_attendance_cty'] = ((combined_total_df['attendance'] / combined_total_df['pop2022']) * 100)
# add new column that rounds up to whole number
combined_total_df['percent_attendance_cty_rounded'] = combined_total_df['percent_attendance_cty']
combined_total_df['percent_attendance_cty_rounded'] = combined_total_df['percent_attendance_cty_rounded'].apply(np.ceil)
# convert percent_attendance_cty_rounded from int type to str type to use discrete colors
combined_total_df['percent_attendance_cty_rounded'] = combined_total_df['percent_attendance_cty_rounded'].astype(str)


# following is for ASC/Nashville
# function for plot #1 (raw attendance)
def plot_continuous_map(column_color, legend_color, rename_label_1, filename):
    map_name = px.choropleth(data_frame=final_df,
                             locations='fips',
                             geojson=counties,
                             color=column_color,
                             color_continuous_scale=legend_color,
                             scope='world',
                             labels={column_color: rename_label_1, 'CTYNAME': 'County name'},
                             hover_data={'fips': False, 'CTYNAME': True}
                             )
    map_name.update_geos(fitbounds="locations", visible=False)
    map_name.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
    map_name.show()
    map_name.write_image("results/" + filename + ".png", scale=6)
    map_name.write_image("results/" + filename + ".svg")


# make plot #1 from above function
plot_continuous_map(column_color='attendance', legend_color='Blues', rename_label_1='Raw attendance', filename='nashville_attendance_raw')

# function for plot #3 (visitors as percent of county population)
def plot_discrete_map(column_color, color_list, legend_list, rename_label_1, filename):
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
    map_name.write_image("results/" + filename + ".png", scale=6)
    map_name.write_image("results/" + filename + ".svg")


# make plot #3 from above function
# convert percent_attendance_cty_rounded from int type to str type to use discrete colors
final_df['percent_attendance_cty_rounded'] = final_df['percent_attendance_cty_rounded'].astype(str)
plot_discrete_map(column_color='percent_attendance_cty_rounded', color_list=['#ffffff', '#e1e2ec', '#c4c6d9', '#a7aac6', '#8b90b3', '#6f76a1', '#525d8f', '#34467d', '#08306b'], legend_list=['0.0', '1.0', '2.0', '3.0', '4.0', '5.0', '6.0', '7.0', '8.0'], rename_label_1='Visitors as a percent of county population', filename='nashville_attendance_percent_county')


# following is for MoSH/Memphis
# function for plot #1 (raw attendance)
def plot_continuous_map(column_color, legend_color, rename_label_1, filename):
    map_name = px.choropleth(data_frame=memp_df,
                             locations='fips',
                             geojson=counties,
                             color=column_color,
                             color_continuous_scale=legend_color,
                             scope='world',
                             labels={column_color: rename_label_1, 'CTYNAME': 'County name'},
                             hover_data={'fips': False, 'CTYNAME': True}
                             )
    map_name.update_geos(fitbounds="locations", visible=False)
    map_name.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
    map_name.show()
    map_name.write_image("results/" + filename + ".png", scale=6)
    map_name.write_image("results/" + filename + ".svg")


# make plot #1 from above function
plot_continuous_map(column_color='attendance', legend_color='Blues', rename_label_1='Raw attendance', filename='memphis_attendance_raw')


# function for plot #3 (visitors as percent of county population)
def plot_discrete_map(column_color, color_list, legend_list, rename_label_1, filename):
    map_name = px.choropleth(data_frame=memp_df,
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
    map_name.write_image("results/" + filename + ".png", scale=6)
    map_name.write_image("results/" + filename + ".svg")


# make plot #3 from above function
# convert percent_attendance_cty_rounded from int type to str type to use discrete colors
memp_df['percent_attendance_cty_rounded'] = memp_df['percent_attendance_cty_rounded'].astype(str)
plot_discrete_map(column_color='percent_attendance_cty_rounded', color_list=['#ffffff', '#e1e2ec', '#c4c6d9', '#a7aac6', '#8b90b3', '#6f76a1', '#525d8f', '#34467d', '#08306b'], legend_list=['0.0', '1.0', '2.0', '3.0', '6.0', '7.0', '9.0', '21.0'], rename_label_1='Visitors as a percent of county population', filename='memphis_attendance_percent_county')


# following is for CDM/Chattanooga
# function for plot #1 (raw attendance)
def plot_continuous_map(column_color, legend_color, rename_label_1, filename):
    map_name = px.choropleth(data_frame=chatt_df,
                             locations='fips',
                             geojson=counties,
                             color=column_color,
                             color_continuous_scale=legend_color,
                             scope='world',
                             labels={column_color: rename_label_1, 'CTYNAME': 'County name'},
                             hover_data={'fips': False, 'CTYNAME': True}
                             )
    map_name.update_geos(fitbounds="locations", visible=False)
    map_name.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
    map_name.show()
    map_name.write_image("results/" + filename + ".png", scale=6)
    map_name.write_image("results/" + filename + ".svg")


# make plot #1 from above function
plot_continuous_map(column_color='attendance', legend_color='Blues', rename_label_1='Raw attendance', filename='chattanooga_attendance_raw')


# function for plot #3 (visitors as percent of county population)
def plot_discrete_map(column_color, color_list, legend_list, rename_label_1, filename):
    map_name = px.choropleth(data_frame=chatt_df,
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
    map_name.write_image("results/" + filename + ".png", scale=6)
    map_name.write_image("results/" + filename + ".svg")


# make plot #3 from above function
plot_discrete_map(column_color='percent_attendance_cty_rounded', color_list=['#ffffff', '#e9eaf1', '#d4d5e3', '#bfc1d5', '#aaadc7', '#9599ba', '#8186ac', '#6c749f', '#576292', '#425085', '#2a4078', '#08306b'], legend_list=['1.0', '2.0', '3.0', '5.0', '6.0', '7.0', '8.0', '9.0', '10.0', '11.0', '16.0', '29.0'], rename_label_1='Visitors as a percent of county population', filename='chattanooga_attendance_percent_county')


# following is for Muse/Knoxville
# function for plot #1 (raw attendance)
def plot_continuous_map(column_color, legend_color, rename_label_1, filename):
    map_name = px.choropleth(data_frame=knox_df,
                             locations='fips',
                             geojson=counties,
                             color=column_color,
                             color_continuous_scale=legend_color,
                             scope='world',
                             labels={column_color: rename_label_1, 'CTYNAME': 'County name'},
                             hover_data={'fips': False, 'CTYNAME': True}
                             )
    map_name.update_geos(fitbounds="locations", visible=False)
    map_name.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
    map_name.show()
    map_name.write_image("results/" + filename + ".png", scale=6)
    map_name.write_image("results/" + filename + ".svg")


# make plot #1 from above function
plot_continuous_map(column_color='attendance', legend_color='Blues', rename_label_1='Raw attendance', filename='knoxville_attendance_raw')


# function for plot #3 (visitors as percent of county population)
def plot_discrete_map(column_color, color_list, legend_list, rename_label_1, filename):
    map_name = px.choropleth(data_frame=knox_df,
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
    map_name.write_image("results/" + filename + ".png", scale=6)
    map_name.write_image("results/" + filename + ".svg")


# make plot #3 from above function
plot_discrete_map(column_color='percent_attendance_cty_rounded', color_list=['#ffffff', '#e1e2ec', '#c4c6d9', '#a7aac6', '#8b90b3', '#6f76a1', '#525d8f', '#34467d', '#08306b'], legend_list=['0.0', '1.0', '2.0', '3.0', '4.0', '6.0', '7.0', '14.0', '19.0'], rename_label_1='Visitors as a percent of county population', filename='knoxville_attendance_percent_county')


# following is for HODC/Johnson City
# function for plot #1 (raw attendance)
def plot_continuous_map(column_color, legend_color, rename_label_1, filename):
    map_name = px.choropleth(data_frame=john_df,
                             locations='fips',
                             geojson=counties,
                             color=column_color,
                             color_continuous_scale=legend_color,
                             scope='world',
                             labels={column_color: rename_label_1, 'CTYNAME': 'County name'},
                             hover_data={'fips': False, 'CTYNAME': True}
                             )
    map_name.update_geos(fitbounds="locations", visible=False)
    map_name.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
    map_name.show()
    map_name.write_image("results/" + filename + ".png", scale=6)
    map_name.write_image("results/" + filename + ".svg")


# make plot #1 from above function
plot_continuous_map(column_color='attendance', legend_color='Blues', rename_label_1='Raw attendance', filename='johnsoncity_attendance_raw')


# function for plot #3 (visitors as percent of county population)
def plot_discrete_map(column_color, color_list, legend_list, rename_label_1, filename):
    map_name = px.choropleth(data_frame=john_df,
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
    map_name.write_image("results/" + filename + ".png", scale=6)
    map_name.write_image("results/" + filename + ".svg")


# make plot #3 from above function
plot_discrete_map(column_color='percent_attendance_cty_rounded', color_list=['#ffffff', '#e1e2ec', '#c4c6d9', '#a7aac6', '#8b90b3', '#6f76a1', '#525d8f', '#34467d', '#08306b'], legend_list=['0.0', '1.0', '2.0', '3.0', '5.0', '6.0', '11.0', '13.0', '21.0'], rename_label_1='Visitors as a percent of county population', filename='johnsoncity_attendance_percent_county')


# following is for DCMS/Murfreesboro
# function for plot #1 (raw attendance)
def plot_continuous_map(column_color, legend_color, rename_label_1, filename):
    map_name = px.choropleth(data_frame=murf_df,
                             locations='fips',
                             geojson=counties,
                             color=column_color,
                             color_continuous_scale=legend_color,
                             scope='world',
                             labels={column_color: rename_label_1, 'CTYNAME': 'County name'},
                             hover_data={'fips': False, 'CTYNAME': True}
                             )
    map_name.update_geos(fitbounds="locations", visible=False)
    map_name.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
    map_name.show()
    map_name.write_image("results/" + filename + ".png", scale=6)
    map_name.write_image("results/" + filename + ".svg")


# make plot #1 from above function
plot_continuous_map(column_color='attendance', legend_color='Blues', rename_label_1='Raw attendance', filename='murfreesboro_attendance_raw')


# function for plot #3 (visitors as percent of county population)
def plot_discrete_map(column_color, color_list, legend_list, rename_label_1, filename):
    map_name = px.choropleth(data_frame=murf_df,
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
    map_name.write_image("results/" + filename + ".png", scale=6)
    map_name.write_image("results/" + filename + ".svg")


# make plot #3 from above function
plot_discrete_map(column_color='percent_attendance_cty_rounded', color_list=['#ffffff', '#d8d9e5', '#b1b4cc', '#8b90b3', '#656e9b', '#3e4e83', '#08306b'], legend_list=['0.0', '1.0', '2.0', '3.0', '4.0', '7.0', '13.0'], rename_label_1='Visitors as a percent of county population', filename='murfreesboro_attendance_percent_county')


# following is for combined centers data
def plot_continuous_map(column_color, legend_color, rename_label_1, filename):
    map_name = px.choropleth(data_frame=combined_total_df,
                             locations='fips',
                             geojson=counties,
                             color=column_color,
                             color_continuous_scale=legend_color,
                             scope='world',
                             labels={column_color: rename_label_1, 'CTYNAME': 'County name'},
                             hover_data={'fips': False, 'CTYNAME': True}
                             )
    map_name.update_geos(fitbounds="locations", visible=False)
    map_name.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
    map_name.show()
    map_name.write_image("results/" + filename + ".png", scale=6)
    map_name.write_image("results/" + filename + ".svg")


# make plot #1 from above function
plot_continuous_map(column_color='attendance', legend_color='Blues', rename_label_1='Raw attendance', filename='combined_attendance_raw')


# function for plot #3 (visitors as percent of county population)
def plot_discrete_map(column_color, color_list, legend_list, rename_label_1, filename):
    map_name = px.choropleth(data_frame=combined_total_df,
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
    map_name.write_image("results/" + filename + ".png", scale=6)
    map_name.write_image("results/" + filename + ".svg")


# make plot #3 from above function
plot_discrete_map(column_color='percent_attendance_cty_rounded', color_list=['#ffffff', '#f2f3f7', '#e6e7ef', '#dadbe7', '#cdcfdf', '#c1c3d7', '#b5b7cf', '#a9acc7', '#9da1bf', '#9195b7', '#858aaf', '#7980a8', '#6d75a0', '#616a98', '#556090', '#495689', '#3c4c81', '#2e427a', '#1f3972', '#08306b'], legend_list=['1.0', '2.0', '3.0', '4.0', '5.0', '6.0', '7.0', '8.0', '9.0', '10.0', '11.0', '12.0', '13.0', '14.0', '15.0', '16.0', '17.0', '21.0', '22.0', '29.0'], rename_label_1='Visitors as a percent of county population', filename='combined_attendance_percent_county')

