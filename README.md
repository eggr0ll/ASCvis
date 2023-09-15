# ASCvis
Initially, 2 maps were proposed:
- One that displays a county's attendance out of the total ASC attendance (as a percent).
- One that displays a county's attendance out of the same county's populations (as a percent).

Later, 2 different maps were decided upon:
- Plot #1: displays a county's raw attendance count using a continuous color scale
- Plot #2: displays a county's attendance out of the same county's population (as a percent).

Both Plot #1 and #2 were made for each ASC and for the combined data from all the centers.

For the county coordinates & other info, I used the `.json` file from plotly's choropleth article (https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json). I got the `fips` codes from https://www.nrcs.usda.gov/wps/portal/nrcs/detail/national/home/?cid=nrcs143_013697.

### 7/11/2022 Meeting

- [x] JP - send slides
- [x] SH - will send data from other ASC by Friday 7/15
- [x] SH - wants #1 and #3 plots
- [x] L - make above plots for each ASC and combined
- [X] L - use blue or red color scheme; straighten out state
- [X] L - eventually make online map filterable by site
- [X] L - use range for legends on plot #3

Sites: Nashville, Murfreesboro, Chattanooga, Memphis, Knoxville, Johnson City

## Dependencies

For writing images to disk, Plotly needs the Kaleido package. Note that at the time of writing, a bug exists in version 0.2.1 that causes a python kernel hang, so install an earlier version:
```
pip install kaleido==0.1.0.post1
```
which is `kaleido-0.1.0.post1-py2.py3-none-win_amd64.whl`
