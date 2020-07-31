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
    print('Usage: %s lat long' % (sys.argv[0]));
    print();
    print('Got:',sys.argv);
    sys.exit(1);

  lat = float(sys.argv[1])
  lon = float(sys.argv[2])

  outFileName = 'test.csv'
  outFile = open(outFileName, 'w');
  outFile.write('Id,Latitude,Longitude\n');
  outFile.write('1' + ',' + str(lat) + ',' + str(lon) + '\n');

  outFile.close()

def auto_PAT():
  path = os.getcwd()
  options = webdriver.ChromeOptions()
  options.add_argument("--headless")
  browser = webdriver.Chrome(path + '/chromedriver', options=options)
  browser.get('https://pat.climatecentral.org/')
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

def create_maps(filename):
  key = "INSERT_KEY"

  with open(filename) as f:
    reader = csv.reader(f, delimiter=",")
    next(reader)
    for i in reader:
      val = float(i[6])
      lis = pincolor(val)
      color = lis[0]
      desc = lis[1]
      gmap=gmplot.GoogleMapPlotter(float(i[1]), float(i[2]), 18, apikey=key, map_type='SATELLITE')
      gmap.marker(float(i[1]), float(i[2]), color=color, info_box_content=desc + " (" + str(val) + ")", display_info_box=True)
    gmap.draw( "2020map.html")

  with open(filename) as f:
    reader = csv.reader(f, delimiter=",")
    next(reader)
    for i in reader:
      val = float(i[7])
      lis = pincolor(val)
      color = lis[0]
      desc = lis[1]
      gmap=gmplot.GoogleMapPlotter(float(i[1]), float(i[2]), 18, apikey=key, map_type='SATELLITE')
      gmap.marker(float(i[1]), float(i[2]), color=color, info_box_content=desc + " (" + str(val) + ")", display_info_box=True)
    gmap.draw( "2030map.html")

  with open(filename) as f:
    reader = csv.reader(f, delimiter=",")
    next(reader)
    for i in reader:
      val = float(i[8])
      lis = pincolor(val)
      color = lis[0]
      desc = lis[1]
      gmap=gmplot.GoogleMapPlotter(float(i[1]), float(i[2]), 18, apikey=key, map_type='SATELLITE')
      gmap.marker(float(i[1]), float(i[2]), color=color, info_box_content=desc + " (" + str(val) + ")", display_info_box=True)
    gmap.draw( "2040map.html")

  with open(filename) as f:
    reader = csv.reader(f, delimiter=",")
    next(reader)
    for i in reader:
      val = float(i[9])
      lis = pincolor(val)
      color = lis[0]
      desc = lis[1]
      gmap=gmplot.GoogleMapPlotter(float(i[1]), float(i[2]), 18, apikey=key, map_type='SATELLITE')
      gmap.marker(float(i[1]), float(i[2]), color=color, info_box_content=desc + " (" + str(val) + ")", display_info_box=True)
    gmap.draw( "2050map.html")

  with open(filename) as f:
    reader = csv.reader(f, delimiter=",")
    next(reader)
    for i in reader:
      val = float(i[10])
      lis = pincolor(val)
      color = lis[0]
      desc = lis[1]
      gmap=gmplot.GoogleMapPlotter(float(i[1]), float(i[2]), 18, apikey=key, map_type='SATELLITE')
      gmap.marker(float(i[1]), float(i[2]), color=color, info_box_content=desc + " (" + str(val) + ")", display_info_box=True)
    gmap.draw( "2060map.html")

  with open(filename) as f:
    reader = csv.reader(f, delimiter=",")
    next(reader)
    for i in reader:
      val = float(i[11])
      lis = pincolor(val)
      color = lis[0]
      desc = lis[1]
      gmap=gmplot.GoogleMapPlotter(float(i[1]), float(i[2]), 18, apikey=key, map_type='SATELLITE')
      gmap.marker(float(i[1]), float(i[2]), color=color, info_box_content=desc + " (" + str(val) + ")", display_info_box=True)
    gmap.draw( "2070map.html")

  with open(filename) as f:
    reader = csv.reader(f, delimiter=",")
    next(reader)
    for i in reader:
      val = float(i[12])
      lis = pincolor(val)
      color = lis[0]
      desc = lis[1]
      gmap=gmplot.GoogleMapPlotter(float(i[1]), float(i[2]), 18, apikey=key, map_type='SATELLITE')
      gmap.marker(float(i[1]), float(i[2]), color=color, info_box_content=desc + " (" + str(val) + ")", display_info_box=True)
    gmap.draw( "2080map.html")

  with open(filename) as f:
    reader = csv.reader(f, delimiter=",")
    next(reader)
    for i in reader:
      val = float(i[13])
      lis = pincolor(val)
      color = lis[0]
      desc = lis[1]
      gmap=gmplot.GoogleMapPlotter(float(i[1]), float(i[2]), 18, apikey=key, map_type='SATELLITE')
      gmap.marker(float(i[1]), float(i[2]), color=color, info_box_content=desc + " (" + str(val) + ")", display_info_box=True)
    gmap.draw( "2090map.html")

  with open(filename) as f:
    reader = csv.reader(f, delimiter=",")
    next(reader)
    for i in reader:
      val = float(i[14])
      lis = pincolor(val)
      color = lis[0]
      desc = lis[1]
      gmap=gmplot.GoogleMapPlotter(float(i[1]), float(i[2]), 18, apikey=key, map_type='SATELLITE')
      gmap.marker(float(i[1]), float(i[2]), color=color, info_box_content=desc + " (" + str(val) + ")", display_info_box=True)
    gmap.draw( "2100map.html")

  
  
  
if __name__=='__main__':
  create_csv()
  filename = auto_PAT()
  create_maps(filename) 
