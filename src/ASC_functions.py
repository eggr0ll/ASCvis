import plotly.express as px
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


def plot_continuous_map(data, column_color, legend_color, rename_label_1, filename, counties):
    """
    Generate a plot for raw attendance
    :param data:
    :param column_color:
    :param legend_color:
    :param rename_label_1:
    :param filename:
    :param counties
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
    map_name.write_image("../results/" + filename + ".png", scale=6)
    map_name.write_image("../results/" + filename + ".svg")


def plot_discrete_map(data, column_color, color_list, legend_list, rename_label_1, filename, counties):
    """
    Generate a plot for visitors as percent of county population, i.e. normalized
    :param data:
    :param column_color:
    :param color_list:
    :param legend_list:
    :param rename_label_1:
    :param filename:
    :param counties
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
    map_name.write_image("../results/" + filename + ".png", scale=6)
    map_name.write_image("../results/" + filename + ".svg")
