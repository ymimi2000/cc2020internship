import csv
import os
import pandas as pd





def tractstate():

	# downloaded from https://www2.census.gov/geo/docs/reference/cenpop2010/tract/CenPop2010_Mean_TR.txt
	df = pd.read_csv("CenPop2010_Mean_TR.csv", dtype={'STATEFP': object, 'COUNTYFP': object, 'TRACTCE': object})
	df['tract_id'] = (df['STATEFP'].map(str) + df['COUNTYFP'].map(str) + df['TRACTCE'].map(str)).astype(int)
	keep_col = ['tract_id','STATEFP']
	new_f = df[keep_col]
	new_f = new_f.rename(columns={"STATEFP": "FIPS"})
	new_f['FIPS'] = new_f['FIPS'].astype(str)
	new_f.to_csv("TractFips.csv", index=False)

	first = pd.read_csv('TractFips.csv', dtype={'FIPS': object})
	second = pd.read_csv('FIPSname.csv', dtype={'FIPS': object})
	merged = pd.merge(first, second, how='left', on='FIPS')

	merged = merged[merged['State'].notna()]
	merged.to_csv('TractState.csv', index=False)



	

if __name__=='__main__':
  tractstate()
