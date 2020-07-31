import sys;
import os
import numpy;
import math 
from shapely.geometry import Point, Polygon
import pandas as pd
# Import gmplot library.
from gmplot import *
from selenium import webdriver
import time
from selenium.webdriver.chrome.options import Options
import csv
import webbrowser
from selenium.webdriver.common.keys import Keys


def create_csv():
  if len(sys.argv) < 3:
    print('Usage: %s meters polygon_vertices.csv' % (sys.argv[0]));
    print();
    print('Got:',sys.argv);
    sys.exit(1);
  
  meters = float(sys.argv[1]);
  outFileName = 'test.csv'

  df = pd.read_csv(sys.argv[2])

  lat1 = df['Lat'].max()
  lon1 = df['Long'].min()
  lat2 = df['Lat'].min()
  lon2 = df['Long'].max()

  # store different polygons and separate data by ID
  all_polygons = []

  for name, group in df.groupby('ID'): 
    #print("ID: ",name)
    #print(group)
    if len(group)>= 3:
        poly = Polygon(zip(group.Lat,group.Long)) #
        all_polygons.append(poly)
        #print(poly.wkt)


  # approximate radius of earth in million meters
  R = 6371000
  
  latList = numpy.empty(0)

  lat = lat1

  while True:
    latList = numpy.append(latList, lat)
    lat = lat - (180/math.pi)*(meters/R)

    if (lat < lat2):
      break


  lonList = numpy.empty(0)

  lon = lon1
  while True:
    lonList = numpy.append(lonList, lon)
    lon = lon + (180/math.pi)*(meters/R)

    if (lon > lon2):
      break


  lonGrid, latGrid = numpy.meshgrid(lonList, latList);
  

  lonGrid = numpy.ndarray.flatten(lonGrid);
  latGrid = numpy.ndarray.flatten(latGrid);
  #print(lonGrid)
  #print(latGrid)

  outFile = open(outFileName, 'w');
  outFile.write('Id,Latitude,Longitude\n');
  
  k = 0
  count = 1
  for i in range(len(lonGrid)):
    p = Point(latGrid[i], lonGrid[i])
    k = 0
    # check if point is in any of the polygons
    for poly in all_polygons:
      if poly.contains(p):
        k = 1
    if k == 1:
      outFile.write(str(count) + ',' + str(latGrid[i]) + ',' + str(lonGrid[i]) + '\n');
      count = count + 1

  dflength = len(df['Lat'])/2
  retLat = df['Lat'][dflength]
  retLon = df['Long'][dflength]


  return retLat,retLon

def auto_PAT():
  path = os.getcwd()
  options = webdriver.ChromeOptions()
  options.add_argument("--headless")
  options.add_argument("--incognito")
  options.add_argument('--ignore-ssl-errors=yes')
  options.add_argument('--ignore-certificate-errors')
  browser = webdriver.Chrome(executable_path=path + '/chromedriver', options=options)
  browser.get('https://pat.climatecentral.org/')
  time.sleep(2)
  apikey = browser.find_element_by_id('apiKey')
  apikey.send_keys('testApiKey123')
  name = browser.find_element_by_id('name')
  name.send_keys('Yazan')
  email = browser.find_element_by_id('email')
  email.send_keys('pat@climatecentral.org')
  file = browser.find_element_by_id('file')
  file.send_keys(path + '/test.csv')
  browser.find_element_by_css_selector(".btn[type='submit']").click()
  time.sleep(4)
  browser.find_elements_by_class_name('modal-close')[2].click()
  time.sleep(4)
  filename = browser.find_element_by_id('jobId').text + ".csv"

  while True:
    if (browser.find_element_by_id('status').text == "COMPLETE"):
      time.sleep(5)
      elementclick = browser.find_element_by_id("file-name").click()
      time.sleep(5)
      break

  return filename

def pincolor(val):
  if 0.01 <= val < 0.1:
    return ["yellow", "Occasional Flood Risk"]
  if 0.1 <= val < 1:
    return ["orange", "Frequent Flood Risk"]
  if 1 <= val:
    return ["red", "Chronic Flood Risk"]
  return ["white", "No Flood Risk"]

def create_maps(filename, lat, lon):
  key = "INSERT_KEY"

  with open(filename) as f:
    reader = csv.reader(f, delimiter=",")
    next(reader)
    gmap=gmplot.GoogleMapPlotter(lat, lon, 18, apikey=key, map_type='SATELLITE')
    for i in reader:
      val = float(i[6])
      lis = pincolor(val)
      color = lis[0]
      desc = lis[1]
      
      gmap.marker(float(i[1]), float(i[2]), color=color, label=str(i[0]))
    gmap.draw( "2020map.html")

  with open(filename) as f:
    reader = csv.reader(f, delimiter=",")
    next(reader)
    gmap=gmplot.GoogleMapPlotter(lat, lon, 18, apikey=key, map_type='SATELLITE')
    for i in reader:
      val = float(i[7])
      lis = pincolor(val)
      color = lis[0]
      desc = lis[1]
      
      gmap.marker(float(i[1]), float(i[2]), color=color, label=str(i[0]))
    gmap.draw( "2030map.html")

  with open(filename) as f:
    reader = csv.reader(f, delimiter=",")
    next(reader)
    gmap=gmplot.GoogleMapPlotter(lat, lon, 18, apikey=key, map_type='SATELLITE')
    for i in reader:
      val = float(i[8])
      lis = pincolor(val)
      color = lis[0]
      desc = lis[1]
      
      gmap.marker(float(i[1]), float(i[2]), color=color, label=str(i[0]))
    gmap.draw( "2040map.html")

  with open(filename) as f:
    reader = csv.reader(f, delimiter=",")
    next(reader)
    gmap=gmplot.GoogleMapPlotter(lat, lon, 18, apikey=key, map_type='SATELLITE')
    for i in reader:
      val = float(i[9])
      lis = pincolor(val)
      color = lis[0]
      desc = lis[1]
      
      gmap.marker(float(i[1]), float(i[2]), color=color, label=str(i[0]))
    gmap.draw( "2050map.html")

  with open(filename) as f:
    reader = csv.reader(f, delimiter=",")
    next(reader)
    gmap=gmplot.GoogleMapPlotter(lat, lon, 18, apikey=key, map_type='SATELLITE')
    for i in reader:
      val = float(i[10])
      lis = pincolor(val)
      color = lis[0]
      desc = lis[1]
      
      gmap.marker(float(i[1]), float(i[2]), color=color, label=str(i[0]))
    gmap.draw( "2060map.html")

  with open(filename) as f:
    reader = csv.reader(f, delimiter=",")
    next(reader)
    gmap=gmplot.GoogleMapPlotter(lat, lon, 18, apikey=key, map_type='SATELLITE')
    for i in reader:
      val = float(i[11])
      lis = pincolor(val)
      color = lis[0]
      desc = lis[1]
      
      gmap.marker(float(i[1]), float(i[2]), color=color, label=str(i[0]))
    gmap.draw( "2070map.html")

  with open(filename) as f:
    reader = csv.reader(f, delimiter=",")
    next(reader)
    gmap=gmplot.GoogleMapPlotter(lat, lon, 18, apikey=key, map_type='SATELLITE')
    for i in reader:
      val = float(i[12])
      lis = pincolor(val)
      color = lis[0]
      desc = lis[1]
      
      gmap.marker(float(i[1]), float(i[2]), color=color, label=str(i[0]))
    gmap.draw( "2080map.html")

  with open(filename) as f:
    reader = csv.reader(f, delimiter=",")
    next(reader)
    gmap=gmplot.GoogleMapPlotter(lat, lon, 18, apikey=key, map_type='SATELLITE')
    for i in reader:
      val = float(i[13])
      lis = pincolor(val)
      color = lis[0]
      desc = lis[1]
      
      gmap.marker(float(i[1]), float(i[2]), color=color, label=str(i[0]))
    gmap.draw( "2090map.html")

  with open(filename) as f:
    reader = csv.reader(f, delimiter=",")
    next(reader)
    gmap=gmplot.GoogleMapPlotter(lat, lon, 18, apikey=key, map_type='SATELLITE')
    for i in reader:
      val = float(i[14])
      lis = pincolor(val)
      color = lis[0]
      desc = lis[1]
      
      gmap.marker(float(i[1]), float(i[2]), color=color, label=str(i[0]))
    gmap.draw( "2100map.html")

  
  
  
if __name__=='__main__':
  lat,lon = create_csv()
  filename = auto_PAT()
  create_maps(filename, lat, lon) 
