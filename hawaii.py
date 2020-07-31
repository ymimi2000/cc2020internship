import csv
import os
import pandas as pd

def hawaii():
	# Taken from https://www.hawaiianelectric.com/documents/clean_energy_hawaii/clean_energy_facts/pv_summary_1Q_2020.pdf
	# Hawaiian Electric = Honolulu County
	# Hawaii Electric Light = Hawaii County
	# Maui Electric =  Maui County
	# downloaded from https://www2.census.gov/geo/docs/reference/cenpop2010/county/CenPop2010_Mean_CO15.txt
	co = pd.read_csv("CenPop2010_Mean_CO15.csv", dtype={'COUNTYFP': object, 'COUNAME': object, 'POPULATION' :object})
	keep_col = ['COUNTYFP','COUNAME','POPULATION']
	co = co[keep_col]
	co = co.rename(columns={"POPULATION": "County_Population"})
	co['County_Capacity'] = [69.3, 307.35, 0, 0, 72.39]
	co.to_csv("CensusCO15modified.csv", index=False)

		# downloaded from https://www2.census.gov/geo/docs/reference/cenpop2010/tract/CenPop2010_Mean_TR15.txt
	tr = pd.read_csv("CenPop2010_Mean_TR15.csv", dtype={'STATEFP': object, 'COUNTYFP': object, 'TRACTCE': object})
	tr['tract_id'] = (tr['STATEFP'].map(str) + tr['COUNTYFP'].map(str) + tr['TRACTCE'].map(str)).astype(int)
	keep_col = ['COUNTYFP','tract_id','POPULATION']
	tr = tr[keep_col]
	tr = tr.rename(columns={"POPULATION": "Tract_Population"})
	tr.to_csv("CensusTR15modified.csv", index=False)

	# downloaded from https://www2.census.gov/geo/docs/reference/cenpop2010/blkgrp/CenPop2010_Mean_BG15.txt
	bg = pd.read_csv("CenPop2010_Mean_BG15.csv", dtype={'STATEFP': object, 'COUNTYFP': object, 'TRACTCE': object})
	bg['tract_id'] = (bg['STATEFP'].map(str) + bg['COUNTYFP'].map(str) + bg['TRACTCE'].map(str)).astype(int)
	keep_col = ['tract_id','BLKGRPCE','POPULATION','LATITUDE', 'LONGITUDE']
	bg = bg[keep_col]
	bg = bg.rename(columns={"POPULATION": "Block_Group_Population", "BLKGRPCE": "Block_Group_Number", 'LATITUDE' : 'Block_Group_LAT', 'LONGITUDE' : 'Block_Group_LON'})
	bg.to_csv("CensusBG15modified.csv", index=False)

	first = pd.read_csv('CensusCO15modified.csv')
	second = pd.read_csv('CensusTR15modified.csv')
	merged = pd.merge(first, second, how='right', on='COUNTYFP')
	merged.to_csv('cenpopCOandTR.csv', index=False)

	#cotr = pd.read_csv("cenpopCOandTR.csv", dtype={'COUNTYFP': object, 'COUNAME': object, 'County_Population' :object, 'Tract_Population' :object,'})
	cotr = pd.read_csv("cenpopCOandTR.csv", dtype ={'Tract_Population': float, 'County_Population': float})
	copop_collection = cotr['Tract_Population'].tolist()
	trpop_collection = cotr['County_Population'].tolist()
	cotr['cotrpopulation_ratio'] = (cotr['Tract_Population']/cotr['County_Population']).astype(float)
	cotr['tract_capacity'] = cotr['cotrpopulation_ratio'] * cotr['County_Capacity']
	cotr.to_csv("cenpopCOandTR.csv", index=False)

if __name__=='__main__':
  hawaii()