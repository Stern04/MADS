#!/usr/bin/env python
# coding: utf-8

# # This notebook created the dbf files that were joined into the ArcGIS map that created a cartogram that showed Covid rates vs Net Energy generation rates. The dbf files came from csv files which came from manipulated Pandas Data Frames in this notebook.

# ### This is the working notebook that was used to manipulate both Covid19 data as well as Net Energy Generation data from EIA. Regrettably, there was not much time left to create a cleaner presentation. Some commenting was used as well as Markdown cells such as this which should make the code somewhat more readable.
#
# ### The main tasks completed in terms of manipulation were summarizing the daily Covid data into a form that could be joined to the ArcGIS State shapefile and was in the same level of detail (interval) as the monthly EIA Net Energy Generation. There was also much manipulation involed in "unpivoting" the EIA data to create montlhy averages and apply them to the 2020 EIA records which resulted in a "% of the norm"
#
# ### Ultimately, the Covid data and Net Gen data were not merged to use in ArcGIS until after there were separately joined in ArcGIS. They were only merged in this notebook at the end where a correlation coefficient was created between the number of covid cases per 100k and the Net Gen for March-July as a % of the average Net Gen. While there was a noticable decrease in Net Gen in earlier "lock down" months, there was almost a 0 correlation coefficeint between these two variables specifically.

# In[2]:


pip install geopandas


# In[3]:


import pandas as pd
import geopandas as gpd
import json
import numpy as np


# In[4]:


pd.set_option('display.max_columns', None)


# In[5]:


ihme_covid = pd.read_csv('Worse_hospitalization_all_locs.csv')
state_names = ["Alaska", "Alabama", "Arkansas", "American Samoa", "Arizona", "California", "Colorado", "Connecticut", "District ", "of Columbia", "Delaware", "Florida", "Georgia", "Guam", "Hawaii", "Iowa", "Idaho", "Illinois", "Indiana", "Kansas", "Kentucky", "Louisiana", "Massachusetts", "Maryland", "Maine", "Michigan", "Minnesota", "Missouri", "Mississippi", "Montana", "North Carolina", "North Dakota", "Nebraska", "New Hampshire", "New Jersey", "New Mexico", "Nevada", "New York", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Puerto Rico", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Virginia", "Virgin Islands", "Vermont", "Washington", "Wisconsin", "West Virginia", "Wyoming"]


# In[6]:


ihme_locations = ihme_covid['location_name'].unique()


# In[7]:


state_matches = [state_names[i] if state_names[i] in ihme_locations else print(state_names[i],' no match')                 for i in range(len(state_names))]


# In[8]:


#take only the rows that pertain to states in state_names AND remove the country of Georgia id 35 as it is also a state name
ihme_covid_US_all = ihme_covid[ihme_covid['location_name'].isin(state_names)]
ihme_covid_US_all = ihme_covid_US_all[ihme_covid_US_all['location_id'] != 35]
# ihme_covid_US_all[ihme_covid_US_all['location_name'] == 'New York']


# In[9]:


ihme_covid_US = ihme_covid_US_all[ihme_covid_US_all['mobility_data_type'] == 'observed']
ihme_covid_US = ihme_covid_US[['location_name','location_id','date','confirmed_infections_p100k_rate']]
ihme_covid_US.fillna(value = {'confirmed_infections_p100k_rate':0}, inplace = True)
ihme_covid_US.reset_index(inplace = True)
ihme_covid_US.drop(columns = 'index', inplace = True)
ihme_covid_US.head()


# In[10]:


ihme_covid_US['Month'] = [str(ihme_covid_US['date'][i]).split('/')[0] for i in range(len(ihme_covid_US))]


# In[11]:


ihme_covid_US.head()


# In[12]:


ihme_covid_US_grouped = ihme_covid_US.groupby(['location_name', 'Month']).mean().reset_index()


# In[13]:


ihme_covid_US_grouped.head(5)


# # Try to run calc on all states

# In[18]:


#Pivot to get the dates as columns
ihme_covid_US_pivot_monthly = ihme_covid_US_grouped.pivot(index = 'location_name',columns = 'Month', values =                                           ['confirmed_infections_p100k_rate']).reset_index()


# In[19]:


ihme_covid_US_pivot_monthly.tail(5)


# In[20]:


ihme_covid_US_pivot_monthly.columns = ihme_covid_US_pivot_monthly.columns.droplevel(0)
ihme_covid_US_pivot_monthly.head()


# In[21]:


columns_renaming = {}
cols = ihme_covid_US_pivot_monthly.columns

for i in range(len(cols)):
    if cols[i] == '':
        columns_renaming[cols[i]] = 'State'
    else:
        columns_renaming[cols[i]] = str(cols[i]) + '_2020'

columns_renaming


# In[22]:


ihme_covid_US_pivot_monthly.rename(columns = columns_renaming, inplace = True)


# In[23]:


ihme_covid_US_pivot_monthly.head()


# In[24]:


#All values are currently strings. convert values for all columns except 'state' to float
cols = ihme_covid_US_pivot_monthly.columns
for i in cols:
    if i != 'State':
        ihme_covid_US_pivot_monthly[i] = ihme_covid_US_pivot_monthly[i].astype(float)

#Fix any new NaN values
columns_na_fix = {}
cols = ihme_covid_US_pivot_monthly.columns

for i in range(len(cols)):
    columns_na_fix[cols[i]] = 0

# columns_na_fix
ihme_covid_US_pivot_monthly.fillna(value = columns_na_fix, inplace = True)


# In[25]:


#write table to csv
ihme_covid_US_pivot_monthly.to_csv('ihme_covid_US_pivot_monthly.csv', index=False)
reread_monthly = pd.read_csv('ihme_covid_US_pivot_monthly.csv')
reread_monthly.head()


# In[26]:


#write table to dbf using geopandas as gpd
gf_monthly = gpd.read_file('ihme_covid_US_pivot_monthly.csv')

cols = gf_monthly.columns
for i in cols:
    print(i)
    if i != 'State':
#         print('loop before convert')
        gf_monthly[i] = gf_monthly[i].astype(float)
#         print('after before convert')

# type(gf['2020-02-08'][0])
gf_monthly.to_file('ihme_covid_US_pivot_monthly.dbf')


# # Import EIA Net Gen data

# In[27]:


eia_netgen_df = pd.read_csv('EIA_Net_generation_for_all_sectors_July_update.csv')
eia_netgen_df.head()


# In[28]:


eia_netgen_df['State'] = [eia_netgen_df['State'][i].split('-')[1] for i in range(len(eia_netgen_df))]
eia_netgen_df.head()


# ## Reduce the data down to the last 5 years before taking an average for each month

# In[29]:


eia_cols = eia_netgen_df.columns
keep_years = ['2015', '2016', '2017', '2018', '2019', '2020']
eia_keep_cols = []

for i in eia_cols:
    year = str(i[:4])
    if year in keep_years:
        eia_keep_cols.append(i)
    elif i == 'State':
        eia_keep_cols.append(i)


# In[30]:


eia_netgen_df = eia_netgen_df[eia_keep_cols]
eia_netgen_df.head()


# ### Try melting

# In[31]:


eia_netgen_melt = eia_netgen_df.melt(id_vars = 'State', var_name = 'Date', value_name = 'Thousand_MWh')


# In[32]:


eia_netgen_melt.head(5)


# ### Add a month column to allow grouping by state and month to take each states avg for the month.
# ### This controls for seasonality

# In[33]:


eia_netgen_melt['Month'] = [eia_netgen_melt['Date'][i][4:] for i in range(len(eia_netgen_melt))]


# In[34]:


eia_netgen_melt.head()


# ### Group by State and month and take the mean of each state over its months

# In[35]:


eia_date_grouped = eia_netgen_melt.groupby(['State', 'Month']).mean().reset_index()


# In[36]:


eia_date_grouped.head(5)


# In[37]:


eia_date_grouped.rename(columns = {'Thousand_MWh':'ThsdMWh_avg'}, inplace = True)


# In[38]:


eia_netgen_melt_merge = eia_netgen_melt.merge(eia_date_grouped, how = 'left',                                               left_on=['State', 'Month'], right_on=['State', 'Month'])


# In[39]:


eia_netgen_melt_merge.head(5)


# ### Calculate average column, then pivot dates back out to prepare to join back to arcgis

# In[40]:


eia_netgen_melt_merge['ThsdMWh_%norm'] = round(eia_netgen_melt_merge['Thousand_MWh']/                                               eia_netgen_melt_merge['ThsdMWh_avg'] * 100, 2)


# In[41]:


eia_netgen_melt_merge.head(50)


# In[42]:


eia_netgen_pivot = eia_netgen_melt_merge.pivot(index = 'State', columns = 'Date', values = 'ThsdMWh_%norm').reset_index()


# In[43]:


# eia_netgen_pivot.columns = eia_netgen_pivot.columns.droplevel(0)


# In[44]:


eia_netgen_pivot.head(50)


# In[45]:


#write table to csv
eia_netgen_pivot.to_csv('eia_netgen_pivot.csv', index=False)
reread = pd.read_csv('eia_netgen_pivot.csv')
reread.columns


# In[46]:


#Read csv back in with geopandas then use geopandas to write file to dbf format
eia_netgen_gf = gpd.read_file('eia_netgen_pivot.csv')
eia_netgen_gf.columns

gf_fix_columns = {}
bad_columns = eia_netgen_gf.columns
# print(bad_columns)
# print(len(bad_columns))
good_columns = reread.columns
# print(len(good_columns))
# print(good_columns)

for i in range(len(bad_columns)-1):
    gf_fix_columns[bad_columns[i]] = good_columns[i]


# In[47]:


eia_netgen_gf.rename(columns = gf_fix_columns, inplace = True)


# In[48]:


eia_netgen_gf.drop([0], inplace = True)


# In[49]:


eia_netgen_gf.head()


# In[50]:


eia_netgen_gf_cols = eia_netgen_gf.columns
for i in eia_netgen_gf_cols:
    if i != 'State':
        eia_netgen_gf[i] = eia_netgen_gf[i].astype(float)


# In[51]:


eia_netgen_gf.to_file('eia_netgen_pivot.dbf',)


# ## Merge covid and EIA netgen dfs to run correlation coefficient

# In[52]:


eia_netgen_melt_merge.head(5)


# In[53]:


#Get only values for 2020 in EIA. Also remove the month of January as it does not exist in the covid data
eia_netgen_melt_merge['year'] = [eia_netgen_melt_merge['Date'][i][:4] for i in range(len(eia_netgen_melt_merge))]


# In[54]:


eia_netgen_2020 = eia_netgen_melt_merge[eia_netgen_melt_merge['year'] == '2020']
eia_netgen_2020 = eia_netgen_2020[(eia_netgen_2020['Month'] != '01') & (eia_netgen_2020['Month'] != '02')]
# eia_netgen_2020['Month'] = [str(eia_netgen_2020['Month'][i])[1:] for i in range(len(eia_netgen_2020))]

month_dict = {}
for i in eia_netgen_2020['Month'].unique():
    month_dict[i] = str(i)[1:]

month_dict

eia_netgen_2020['Month'] = [month_dict[i] for i in eia_netgen_2020['Month']]


# In[55]:


eia_netgen_2020.head()


# In[56]:


ihme_covid_US_grouped.head(5)


# In[57]:


#Reduce covid df down to month 7 as the eai data is only months 3-7
include_months = ['3', '4', '5', '6', '7']
# ihme_covid_US_eai_months = ihme_covid_US_grouped[True if ihme_covid_US_grouped['Month'][i] in include_months \
#                                                  for i in range(len(ihme_covid_US_grouped))]

ihme_covid_US_eia_months = ihme_covid_US_grouped[ihme_covid_US_grouped['Month'].isin(include_months)]


# In[58]:


ihme_covid_US_eia_months.tail()


# In[59]:


#Give covid state names corresponding abbreviations to join dia data to.
us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'American Samoa': 'AS',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Guam': 'GU',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands':'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}


# In[60]:


ihme_covid_US_eia_months['State'] = [us_state_abbrev[i] for i in ihme_covid_US_eia_months['location_name']]


# In[61]:


ihme_covid_US_eia_months[ihme_covid_US_eia_months['State'] == 'NY']


# In[62]:


eia_netgen_2020[eia_netgen_2020['State'] == 'NY']


# ### Merge covid data with eia data on combination of state abbrev and month columns and calc r squared

# In[63]:


ihme_covid_US_eia_netgen = ihme_covid_US_eia_months.merge(eia_netgen_2020, on = ['State', 'Month'], how = 'inner')


# In[73]:


ihme_covid_US_eia_netgen_ny = ihme_covid_US_eia_netgen[ihme_covid_US_eia_netgen['State'] == 'FL']


# In[74]:


line_fig = px.line(ihme_covid_US_eia_netgen_ny, y = 'ThsdMWh_%norm', x = 'Date')
line_fig.show()


# In[75]:


regression_line = px.scatter(ihme_covid_US_eia_netgen,
                             x = 'confirmed_infections_p100k_rate', y = 'ThsdMWh_%norm', trendline = 'ols')
regression_line.show()


# In[76]:


results = px.get_trendline_results(regression_line)
print(results)

results.px_fit_results.iloc[0].summary()


# In[ ]:
