import csv
import os
import pandas as pd



def TTSStep1():
	# Downloaded from TTS Website
	f=pd.read_csv("TTS_LBNL_public_file_10-Dec-2019_p1.csv")
	keep_col = ['System Size','Zip Code','State']
	f = f[keep_col]
	lst = ['AZ', 'CA']
	f = f[f['State'].isin(lst)]
	indexNames = f[f['System Size'] > 1190].index
	f.drop(indexNames , inplace=True)
	indexNames = f[f['Zip Code'] == -9999].index
	f.drop(indexNames , inplace=True)
	indexNames = f[f['Zip Code'] == '-9999'].index
	f.drop(indexNames , inplace=True)
	f.to_csv("TTSPart1Modified.csv", index=False)

	f=pd.read_csv("TTS_LBNL_public_file_10-Dec-2019_p2.csv", encoding='latin-1')
	keep_col = ['System Size','Zip Code','State']
	f = f[keep_col]
	lst = ['CA', 'CT', 'DC', 'DE', 'MA', 'MO', 'NH', 'NJ', 'NM', 'NY', 'OH', 'PA', 'VT']
	f = f[f['State'].isin(lst)]
	indexNames = f[f['System Size'] > 1190].index
	f.drop(indexNames , inplace=True)
	indexNames = f[f['Zip Code'] == -9999].index
	f.drop(indexNames , inplace=True)
	indexNames = f[f['Zip Code'] == '-9999'].index
	f.drop(indexNames , inplace=True)
	f.to_csv("TTSPart2Modified.csv", index=False)

	first = pd.read_csv('TTSPart1Modified.csv')
	second = pd.read_csv('TTSPart2Modified.csv')
	merged = pd.merge(first, second, how='outer')
	merged.to_csv('TTSDatabase.csv', index=False)

	os.system("rm -f TTSPart1Modified.csv")
	os.system("rm -f TTSPart2Modified.csv")


	# Downloaded from https://docs.google.com/spreadsheets/d/1ZrfIo6spANQM_C_wekn73sA8JGJ7FWFfzas2sB9fvFE/edit#gid=2602309
	f=pd.read_csv("zipZCTA.csv")
	f = f.rename(columns={"ZIP_CODE": "Zip Code"})
	f.to_csv("zipZCTA2.csv", index=False)
	first = pd.read_csv('TTSDatabase.csv', encoding='latin-1')
	second = pd.read_csv('zipZCTA2.csv', encoding='latin-1')
	first['Zip Code'] = first['Zip Code'].astype(str).apply(lambda x: x.split('-')[0]).astype(int)
	first['Zip Code'] = first['Zip Code'].astype(int)
	merged = pd.merge(first, second, how='left', on='Zip Code')
	merged['ZCTA'] = merged['ZCTA'].round(decimals=0).astype(object)

	merged.to_csv('Step1TTS.csv', index=True)

	os.system("rm -f zipZCTA2.csv")
	os.system("rm -f TTSDatabase.csv")

def TTSStep2():
	
	f=pd.read_csv("Step1TTS.csv")
	f = f.groupby(['ZCTA'])['System Size'].sum()
	f.to_csv("Step2ZCTAcapacity.csv", index=True)

def TTSStep3():
	# Downloaded from https://www2.census.gov/geo/docs/maps-data/data/rel/zcta_tract_rel_10.txt
	f=pd.read_csv("zcta_tract_rel_10.csv")
	# ZPOPPCT: The Percentage of Total Population of the 2010 ZCTA represented by the record
	keep_col = ['ZCTA5','STATE','GEOID','ZPOPPCT']
	f = f[keep_col]
	f = f.rename(columns={"GEOID": "tract_id", 'ZCTA5': 'ZCTA'})
	df = pd.read_csv('Step2ZCTAcapacity.csv')
	f = pd.merge(f, df, how='left', on='ZCTA')
	lst = ['4', '6', '9', '10', '11' ,'25', '29', '33', '34', '35', '36', '39', '42', '50']
	f['STATE'] = f['STATE'].astype(str)
	f = f[f['STATE'].isin(lst)]
	f['Tract Capacity'] = (f['ZPOPPCT']/100) * f['System Size']
	f = f.groupby(['tract_id'])['Tract Capacity'].sum()
	f.to_csv("Step3ZCTAtractREL.csv", index=True)

def TTSStep4():

	# downloaded from https://www2.census.gov/geo/docs/reference/cenpop2010/blkgrp/CenPop2010_Mean_BG.txt
	df = pd.read_csv("CenPop2010_Mean_BG.csv", dtype={'STATEFP': object, 'COUNTYFP': object, 'TRACTCE': object})
	df['tract_id'] = (df['STATEFP'].map(str) + df['COUNTYFP'].map(str) + df['TRACTCE'].map(str)).astype(int)
	keep_col = ['tract_id','BLKGRPCE','POPULATION','LATITUDE', 'LONGITUDE']
	new_f = df[keep_col]
	new_f = new_f.rename(columns={"POPULATION": "Block_Group_Population", "BLKGRPCE": "Block_Group_Number", 'LATITUDE' : 'Block_Group_LAT', 'LONGITUDE' : 'Block_Group_LON'})
	new_f.to_csv("CensusBGmodified.csv", index=False)

	# downloaded from https://www2.census.gov/geo/docs/reference/cenpop2010/tract/CenPop2010_Mean_TR.txt
	df = pd.read_csv("CenPop2010_Mean_TR.csv", dtype={'STATEFP': object, 'COUNTYFP': object, 'TRACTCE': object})
	df['tract_id'] = (df['STATEFP'].map(str) + df['COUNTYFP'].map(str) + df['TRACTCE'].map(str)).astype(int)
	keep_col = ['tract_id','POPULATION']
	new_f = df[keep_col]
	new_f = new_f.rename(columns={"POPULATION": "Tract_Population"})
	new_f.to_csv("CensusTRmodified.csv", index=False)


	first = pd.read_csv('CensusTRmodified.csv')
	second = pd.read_csv('CensusBGmodified.csv')
	merged = pd.merge(first, second, how='left', on='tract_id')
	merged.to_csv('CensusTRBG.csv', index=False)

	
	os.system("rm -f CensusBGmodified.csv")
	os.system("rm -f CensusTRmodified.csv")

	first = pd.read_csv('CensusTRBG.csv')
	second = pd.read_csv('Step3ZCTAtractREL.csv')
	merged = pd.merge(first, second, how='left', on='tract_id')
	merged.to_csv('CensusTRBGcap.csv', index=False)

	os.system("rm -f CensusTRBG.csv")

	f=pd.read_csv("CensusTRBGcap.csv")

	f['population_ratio'] = f['Block_Group_Population']/f['Tract_Population']

	f['block_group_capacity'] = f['population_ratio'] * f['Tract Capacity']

	f = f[f['Tract Capacity'].notna()]

	keep_col = ['tract_id','Block_Group_Number','Block_Group_LAT','Block_Group_LON', 'Tract Capacity', 'block_group_capacity']
	f = f[keep_col]
	f['Source'] = 'TTS_2019'

	f.to_csv('TTSDatabase.csv', index=False)

	os.system("rm -f Step3ZCTAtractREL.csv")
	os.system("rm -f Step2ZCTAcapacity.csv")
	os.system("rm -f Step1TTS.csv")
	os.system("rm -f CensusTRBGcap.csv")

def PSunroof():
	# Downloaded from Google Project Sunroof Website
	f=pd.read_csv("project-sunroof.csv")
	keep_col = ['region_name','state_name','existing_installs_count','count_qualified', 'kw_total']
	new_f = f[keep_col]
	new_f = new_f.rename(columns={"region_name": "tract_id"})
	new_f.to_csv("sunroofmodified.csv", index=False)

	# downloaded from https://www2.census.gov/geo/docs/reference/cenpop2010/blkgrp/CenPop2010_Mean_BG.txt
	df = pd.read_csv("CenPop2010_Mean_BG.csv", dtype={'STATEFP': object, 'COUNTYFP': object, 'TRACTCE': object})
	df['tract_id'] = (df['STATEFP'].map(str) + df['COUNTYFP'].map(str) + df['TRACTCE'].map(str)).astype(int)
	keep_col = ['tract_id','BLKGRPCE','POPULATION','LATITUDE', 'LONGITUDE']
	new_f = df[keep_col]
	new_f = new_f.rename(columns={"POPULATION": "Block_Group_Population", "BLKGRPCE": "Block_Group_Number", 'LATITUDE' : 'Block_Group_LAT', 'LONGITUDE' : 'Block_Group_LON'})
	new_f.to_csv("CensusBGmodified.csv", index=False)

	# downloaded from https://www2.census.gov/geo/docs/reference/cenpop2010/tract/CenPop2010_Mean_TR.txt
	df = pd.read_csv("CenPop2010_Mean_TR.csv", dtype={'STATEFP': object, 'COUNTYFP': object, 'TRACTCE': object})
	df['tract_id'] = (df['STATEFP'].map(str) + df['COUNTYFP'].map(str) + df['TRACTCE'].map(str)).astype(int)
	keep_col = ['tract_id','POPULATION']
	new_f = df[keep_col]
	new_f = new_f.rename(columns={"POPULATION": "Tract_Population"})
	new_f.to_csv("CensusTRmodified.csv", index=False)


	first = pd.read_csv('sunroofmodified.csv')
	second = pd.read_csv('CensusBGmodified.csv')


	merged = pd.merge(first, second, how='left', on='tract_id')
	merged.to_csv('ProjectSunroofDatabase.csv', index=False)

	first = pd.read_csv('ProjectSunroofDatabase.csv')
	second = pd.read_csv('CensusTRmodified.csv')
	merged = pd.merge(first, second, how='left', on='tract_id')
	merged.to_csv('ProjectSunroofDatabase.csv', index=False)

	os.system("rm -f sunroofmodified.csv")
	os.system("rm -f CensusBGmodified.csv")
	os.system("rm -f CensusTRmodified.csv")

	f=pd.read_csv("ProjectSunroofDatabase.csv")

	f['population_ratio'] = f['Block_Group_Population']/f['Tract_Population']

	f['tract_capacity'] = (f['existing_installs_count']/f['count_qualified'])*f['kw_total']

	f['block_group_capacity'] = f['population_ratio'] * f['tract_capacity']

	f.to_csv('ProjectSunroofDatabase.csv', index=False)

	lst = ['Alaska','Alabama','Arkansas','Colorado','Florida','Georgia','Idaho','Iliinois','Indiana','Iowa','Kansas','Kentucky','Louisiana','Maine','Maryland','Michigan', 'Minnesota', 'Mississippi','Montana','Nebraska','Nevada','North Carolina','North Dakota','Oklahoma','Oregon','Rhode Island','South Carolina','South Dakota','Tennessee','Texas','Utah','Virginia','Washington','West Virginia','Wisconsin','Wyoming']

	f=pd.read_csv("ProjectSunroofDatabase.csv")

	f = f[f['state_name'].isin(lst)]

	keep_col = ['tract_id','Block_Group_Number','Block_Group_LAT','Block_Group_LON', 'tract_capacity', 'block_group_capacity']

	f = f[keep_col]
	f = f.rename(columns={"tract_capacity": "Tract Capacity"})

	f['Source'] = 'Project Sunroof'

	f.to_csv('ProjectSunroofDatabase.csv', index=False)

def mergeall():
	first = pd.read_csv('ProjectSunroofDatabase.csv')
	second = pd.read_csv('TTSDatabase.csv')
	merged = pd.merge(first, second, how='outer')
	merged = merged[merged['block_group_capacity'].notna()]
	merged.to_csv('Database.csv', index=False)

	os.system("rm -f ProjectSunroofDatabase.csv")
	os.system("rm -f TTSDatabase.csv")


	

if __name__=='__main__':
  TTSStep1()
  TTSStep2()
  TTSStep3()
  TTSStep4()
  PSunroof()
  mergeall()
