import plotly.express as px
import requests
import json
import pandas as pd
import numpy as np

#
# Functions
#
def hex_to_rgb(hex_str):
    """
    #FFFFFF -> [255,255,255]
    Pass 16 to the integer function for change of base
    """
    return [int(hex_str[i:i+2], 16) for i in range(1,6,2)]


def get_color_gradient(c1, c2, n):
    """
    Given two hex colors, returns a color gradient with n colors
    """
    assert n > 1
    c1_rgb = np.array(hex_to_rgb(c1))/255
    c2_rgb = np.array(hex_to_rgb(c2))/255
    mix_pcts = [x/(n-1) for x in range(n)]
    rgb_colors = [((1-mix)*c1_rgb + (mix*c2_rgb)) for mix in mix_pcts]
    return ["#" + "".join([format(int(round(val*255)), "02x") for val in item]) for item in rgb_colors]


# plot - raw attendance
def plot_continuous_map(data, column_color, legend_color, rename_label_1, filename):
    """
    Generate a plot for raw attendance
    :param data:
    :param column_color:
    :param legend_color:
    :param rename_label_1:
    :param filename:
    :return:
    """
    map_name = px.choropleth(data_frame=data,
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


# plot -
def plot_discrete_map(data, column_color, color_list, legend_list, rename_label_1, filename):
    """
    Generate a plot for visitors as percent of county population, i.e. normalized
    :param data:
    :param column_color:
    :param color_list:
    :param legend_list:
    :param rename_label_1:
    :param filename:
    :return:
    """
    map_name = px.choropleth(data_frame=data,
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

#
# Set up colors
#
# AdvSciCtr branding has #00acbb  but let's do a little darker with #0199A7
#
# get_color_gradient('#dafcff', '#00acbb', 6)
# get_color_gradient('#dafcff', '#0199A7', 6)
#  ['#dafcff', '#aeecf1', '#83dce4', '#57ccd6', '#2cbcc9', '#00acbb'] == native
# ['#dafcff', '#afe8ed', '#83d4dc', '#58c1ca', '#2cadb9', '#0199a7'] == darker
colorscale_blues = [
    [0, '#dafcff'],
    [0.1, '#afe8ed'],
    [0.2, '#83d4dc'],
    [0.4, '#58c1ca'],
    [0.8, '#2cadb9'],
    [1, '#0199a7']
]

#
# Data setup
#
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
# convert percent_attendance_cty_rounded from int type to str type to use discrete colors
final_df['percent_attendance_cty_rounded'] = final_df['percent_attendance_cty_rounded'].astype(str)

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

#
# Nashville
#
plot_continuous_map(data=final_df, column_color='attendance', legend_color=colorscale_blues, rename_label_1='Raw attendance', filename='nashville_attendance_raw')
plot_discrete_map(data=final_df, column_color='percent_attendance_cty_rounded', color_list=get_color_gradient('#dafcff', '#0199A7', 9), legend_list=['0.0', '1.0', '2.0', '3.0', '4.0', '5.0', '6.0', '7.0', '8.0'], rename_label_1='Visitors as a percent of county population', filename='nashville_attendance_percent_county')

#
# MoSH/Memphis
#
plot_continuous_map(data=memp_df, column_color='attendance', legend_color=colorscale_blues, rename_label_1='Raw attendance', filename='memphis_attendance_raw')
plot_discrete_map(data=memp_df, column_color='percent_attendance_cty_rounded', color_list=get_color_gradient('#dafcff', '#0199A7', 9), legend_list=['0.0', '1.0', '2.0', '3.0', '6.0', '7.0', '9.0', '21.0'], rename_label_1='Visitors as a percent of county population', filename='memphis_attendance_percent_county')

#
# Chattanooga
#
plot_continuous_map(data=chatt_df, column_color='attendance', legend_color=colorscale_blues, rename_label_1='Raw attendance', filename='chattanooga_attendance_raw')
plot_discrete_map(data=chatt_df, column_color='percent_attendance_cty_rounded', color_list=get_color_gradient('#dafcff', '#0199A7', 12), legend_list=['1.0', '2.0', '3.0', '5.0', '6.0', '7.0', '8.0', '9.0', '10.0', '11.0', '16.0', '29.0'], rename_label_1='Visitors as a percent of county population', filename='chattanooga_attendance_percent_county')

#
# Muse/Knoxville
#
plot_continuous_map(data=knox_df, column_color='attendance', legend_color=colorscale_blues, rename_label_1='Raw attendance', filename='knoxville_attendance_raw')
plot_discrete_map(data=knox_df, column_color='percent_attendance_cty_rounded', color_list=get_color_gradient('#dafcff', '#0199A7', 9), legend_list=['0.0', '1.0', '2.0', '3.0', '4.0', '6.0', '7.0', '14.0', '19.0'], rename_label_1='Visitors as a percent of county population', filename='knoxville_attendance_percent_county')

#
# HODC/Johnson City
#
plot_continuous_map(data=john_df, column_color='attendance', legend_color=colorscale_blues, rename_label_1='Raw attendance', filename='johnsoncity_attendance_raw')
plot_discrete_map(data=john_df, column_color='percent_attendance_cty_rounded', color_list=get_color_gradient('#dafcff', '#0199A7', 9), legend_list=['0.0', '1.0', '2.0', '3.0', '5.0', '6.0', '11.0', '13.0', '21.0'], rename_label_1='Visitors as a percent of county population', filename='johnsoncity_attendance_percent_county')

#
#  DCMS/Murfreesboro
#
plot_continuous_map(data=murf_df, column_color='attendance', legend_color=colorscale_blues, rename_label_1='Raw attendance', filename='murfreesboro_attendance_raw')
plot_discrete_map(data=murf_df, column_color='percent_attendance_cty_rounded', color_list=get_color_gradient('#dafcff', '#0199A7', 7), legend_list=['0.0', '1.0', '2.0', '3.0', '4.0', '7.0', '13.0'], rename_label_1='Visitors as a percent of county population', filename='murfreesboro_attendance_percent_county')


#
# Combined centers data
#
plot_continuous_map(data=combined_total_df, column_color='attendance', legend_color=colorscale_blues, rename_label_1='Raw attendance', filename='combined_attendance_raw')
plot_discrete_map(data=combined_total_df, column_color='percent_attendance_cty_rounded', color_list=get_color_gradient('#dafcff', '#0199A7', 20), legend_list=['1.0', '2.0', '3.0', '4.0', '5.0', '6.0', '7.0', '8.0', '9.0', '10.0', '11.0', '12.0', '13.0', '14.0', '15.0', '16.0', '17.0', '21.0', '22.0', '29.0'], rename_label_1='Visitors as a percent of county population', filename='combined_attendance_percent_county')
