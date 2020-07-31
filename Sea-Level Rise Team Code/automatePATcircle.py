import sys;
import os
import numpy;
import math 
from shapely.geometry import Point, Polygon
import shapely
import pandas as pd
# Import gmplot library.
from gmplot import *
from selenium import webdriver
import time
from selenium.webdriver.chrome.options import Options
import csv
import webbrowser
from selenium.webdriver.common.keys import Keys
from PIL import Image, ImageDraw, ImageFont
import imageio



def create_csv():
  if len(sys.argv) < 5:
    print('Usage: %s gridmeters radiusmeters lat lon' % (sys.argv[0]));
    print();
    print('Got:',sys.argv);
    sys.exit(1);

  meters = float(sys.argv[1]);
  rmeters = float(sys.argv[2])
  lat0 = float(sys.argv[3])
  lon0 = float(sys.argv[4])
  outFileName = 'test.csv'

  # approximate radius of earth in million meters
  R = 6371000


  lat1 = lat0 + (180/math.pi)*(rmeters/R)
  lon1 = lon0 - (180/math.pi)*(rmeters/R)* math.cos((lat1*(math.pi/180)))
  lat2 = lat0 - (180/math.pi)*(rmeters/R)
  lon2 = lon0 + (180/math.pi)*(rmeters/R)* math.cos((lat2*(math.pi/180)))

  circle = Point(lat0, lon0).buffer(1)
  ellipse = shapely.affinity.scale(circle, (180/math.pi)*(rmeters/R), (180/math.pi)*(rmeters/R))

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

  count = 1
  for i in range(len(lonGrid)):
    lonGrid[i] = lonGrid[i] * math.cos((latGrid[i]*(math.pi/180)))
    p = Point(latGrid[i], lonGrid[i])
    #if ellipse.contains(p):
    outFile.write(str(count) + ',' + str(latGrid[i]) + ',' + str(lonGrid[i]) + '\n');
    count = count + 1

  return lat0,lon0

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
  zoom = 16

  with open(filename) as f:
    reader = csv.reader(f, delimiter=",")
    next(reader)
    gmap=gmplot.GoogleMapPlotter(lat, lon, zoom, apikey=key, map_type='SATELLITE')
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
    gmap=gmplot.GoogleMapPlotter(lat, lon, zoom, apikey=key, map_type='SATELLITE')
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
    gmap=gmplot.GoogleMapPlotter(lat, lon, zoom, apikey=key, map_type='SATELLITE')
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
    gmap=gmplot.GoogleMapPlotter(lat, lon, zoom, apikey=key, map_type='SATELLITE')
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
    gmap=gmplot.GoogleMapPlotter(lat, lon, zoom, apikey=key, map_type='SATELLITE')
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
    gmap=gmplot.GoogleMapPlotter(lat, lon, zoom, apikey=key, map_type='SATELLITE')
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
    gmap=gmplot.GoogleMapPlotter(lat, lon, zoom, apikey=key, map_type='SATELLITE')
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
    gmap=gmplot.GoogleMapPlotter(lat, lon, zoom, apikey=key, map_type='SATELLITE')
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
    gmap=gmplot.GoogleMapPlotter(lat, lon, zoom, apikey=key, map_type='SATELLITE')
    for i in reader:
      val = float(i[14])
      lis = pincolor(val)
      color = lis[0]
      desc = lis[1]
      
      gmap.marker(float(i[1]), float(i[2]), color=color, label=str(i[0]))
    gmap.draw( "2100map.html")

def fullpage_screenshot():
    path = os.getcwd()
    for filename in os.listdir(path):
      if filename.endswith('.html'):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--start-maximized')
        driver = webdriver.Chrome(executable_path=path + '/chromedriver', options=chrome_options)
        driver.get("file://" + path + "/" + filename)
        time.sleep(2)

        driver.save_screenshot(filename.replace(".html", "") + ".png")
        driver.quit()

    for filename in os.listdir(path):
      if filename.endswith('.png'):
        # create Image object with the input image

        image = Image.open(filename)

        # initialise the drawing context with
        # the image object as background

        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype('/Library/Fonts/Arial.ttf', size=45)

      # starting position of the message

        (x, y) = (20, 100)
        message = filename.replace(".png", "").replace("map", " Map")
        color = 'rgb(255, 255, 255)' # black color

        # draw the message on the background

        draw.text((x, y), message, fill=color, font=font)
        image.save(filename)

    images = []
    images.append(imageio.imread("2020map.png"))
    images.append(imageio.imread("2030map.png"))
    images.append(imageio.imread("2040map.png"))
    images.append(imageio.imread("2050map.png"))
    images.append(imageio.imread("2060map.png"))
    images.append(imageio.imread("2070map.png"))
    images.append(imageio.imread("2080map.png"))
    images.append(imageio.imread("2090map.png"))
    images.append(imageio.imread("2100map.png"))
    imageio.mimsave('maps.gif', images, 'GIF', duration=1)
    os.system('rm *.png')
  
  
  
if __name__=='__main__':
  lat,lon = create_csv()
  filename = auto_PAT()
  create_maps(filename, lat, lon)
  fullpage_screenshot() 
