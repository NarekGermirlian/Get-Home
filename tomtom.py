import json
import urllib.request
from PIL import Image
import math
import folium
import webbrowser
import random
import os

import configparser

Config = configparser.ConfigParser()
Config.read("config.ini")

API_KEY = Config.get('TomTom', 'API_KEY')

#Setting image size using a diciontary
switcher = {
  'small': 'width=256&height=256',
  'medium': 'width=512&height=512',
  'large': 'width=1024&height=1024',
}
latitude = 34.24370037756628
longitude = -118.49894193709267

# Methods
def findRandomCoords(homeCoords: tuple[float, float], radius: int) -> tuple[float, float]:
   randTheta = random.randrange(0,360)
   randThetaRadians = randTheta*math.pi/180
   #Random value between 0-difficulty mile(s), and whatever that is in coordinate system length

   randRadius = random.random()*int(radius)/69   # One degree latitude is about 69 miles

   randXCoord = homeCoords[0] + (randRadius*math.cos(randThetaRadians))
   randYCoord = homeCoords[1] + (randRadius*math.sin(randThetaRadians))

   return (randXCoord, randYCoord)

def createFoliumMap(homeAdd: str, homeCoord: tuple, randAdd: str, randCoord: tuple, zoom: int):
   #Middle point to center map
   centerXCoord = (homeCoord[0]+randCoord[0])/2
   centerYCoord = (homeCoord[1]+randCoord[1])/2

   #Create map
   m = folium.Map(location=(centerXCoord, centerYCoord),zoom_start=zoom)

   #Marker for home
   folium.Marker(homeCoord,
                 popup='<h1>'+homeAdd+'</h1><p>This is your destination.</p>', # When you click it, gives more information
                 tooltip='Home', # When you hover over it, gives information
                 icon=folium.Icon(icon='flag',color='black',icon_color='green')).add_to(m)
   
   #Marker for random address
   folium.Marker(randCoord,
                 popup='<h1>'+randAdd+'</h1><p>You begin here</p>', # When you click it, gives more information
                 tooltip='This is a random Location', # When you hover over it, gives information
                 icon=folium.Icon(icon='home',color='red',icon_color='black')).add_to(m)
   
   
   #folium.PolyLine()

   local_path = "Maps/map.html"
   m.save(local_path)

   #Display map on user's end
   webbrowser.open_new_tab(os.path.abspath(local_path))

   '''
   #Showing the path on the map (not currently finished):
   trail_coordinates = []

   folium.Polyline(trail_coordinates, tooltip='route').add_to(m)
   '''

def createNewAddress() -> dict:
    resp = {}
    resp['streetNum'] = input("Please input street number: ").replace(' ', '_')
    resp['streetName'] = input("Please input street name: ").replace(' ', '_')
    resp['city'] = input("Please input city: ").replace(' ', '_')
    resp['state'] = input("Please input state: ").replace(' ', '_')
    resp['zip'] = input("Please input postal address: ").replace(' ', '_')

    return resp

def structuredGeocode(resp: dict) -> dict:
    structuredGeocodingURL = 'https://api.tomtom.com/search/2/structuredGeocode.json?key='+API_KEY+'&countryCode=US&streetNumber='+resp['streetNum']+'&streetName='+resp['streetName']+'&municipality='+resp['city']+'&countrySubdivision='+resp['state']+'&postalCode='+resp['zip']+'&language=en-US'
    structuredGeocodingReq = urllib.request.urlopen(structuredGeocodingURL)
    structuredGeocodingData = structuredGeocodingReq.read().decode('utf-8')
    structuredGeocodingJSON = json.loads(structuredGeocodingData)

    return structuredGeocodingJSON

def reverseGeocode(lat: str, lon: str) -> str:
    url = 'https://api.tomtom.com/search/2/reverseGeocode/'+str(lat)+','+str(lon)+'.json?key='+API_KEY+'&language=en-US'
    req = urllib.request.urlopen(url)
    data = req.read().decode('utf-8')
    JSONdata = json.loads(data)
    if 'freeformAddress' not in JSONdata['addresses'][0]['address']:
       return 'No address found'
    address = JSONdata['addresses'][0]['address']['freeformAddress']
    return address

def getStillSnap(lat: str, lon: str, zoom: int,fileName: str,size='large') -> None:
  #Zoom is auto-selected to ensure that both houses are displayed within the capture
  urlStaticImage = 'https://api.tomtom.com/map/1/staticimage?key='+API_KEY+'&layer=hybrid&zoom='+str(zoom)+'&center='+str(lon)+','+str(lat)+'&format=png&layer=basic&style=main&'+str(switcher.get(size))+'&view=Unified&language=en-GB'
  
  #Save image to a file
  save_path = "C:/Users/ngerm/Desktop/Coding/Python/GetHome/Images/"+str(fileName)+'.png'
  urllib.request.urlretrieve(urlStaticImage, save_path)

  #Open image
  img = Image.open(save_path)
  img.show()

def getStillSnapBoundary(lat1: float, lon1: float, lat2: float, lon2: float, fileName: str) -> None:
  #Finding min lat and lon
  minLat = str(min([lat1, lat2]))
  minLon = str(min([lon1,lon2]))
  maxLat = str(max([lat1, lat2]))
  maxLon = str(max([lon1, lon2]))

  zoom = input("Input zoom level (0 to 22): ")
  #size = input("Input size (small, medium, large): ")
  urlStaticImage = 'https://api.tomtom.com/map/1/staticimage?key='+API_KEY+'&zoom='+zoom+'&bbox='+minLon+','+minLat+','+maxLon+','+maxLat+'&format=jpg&layer=basic&style=main&&view=Unified&language=en-US'

  print(urlStaticImage)
  #Save image to a file
  save_path = "C:/Users/ngerm/Desktop/Coding/Python/GetHome/Images/"+str(fileName)+'.png'
  urllib.request.urlretrieve(urlStaticImage, save_path)

  #Open image
  img = Image.open(save_path)
  img.show()

def getRoutes(startCoord: str, endCoord: str) -> dict:
    url = 'https://api.tomtom.com/routing/1/calculateRoute/\
'+startCoord.replace(' ','')+':'+endCoord.replace(' ','')+'/json?\
&instructionsType=text&language=en-US\
&sectionType=traffic\
&report=effectiveSettings\
&routeRepresentation=polyline\
&traffic=true&avoid=unpavedRoads\
&travelMode=car&vehicleMaxSpeed=120\
&vehicleCommercial=false&vehicleEngineType=combustion\
&maxAlternatives=5\
&key=' + API_KEY
    
    req = urllib.request.urlopen(url)
    routeData = req.read().decode('utf-8')
    routeJSON = json.loads(routeData)

    routes = {}
    route = []
    routeCount=0
    
    routeInstructions = routeJSON['routes']

    for routeInstruction in routeInstructions:
        route=[]
        routeCount+=1
        for instruction in routeInstruction['guidance']['instructions']:
            if 'street' not in instruction:
                continue

            street = instruction['street']
            if street in route:
                if route.index(street)!=(len(route)-1):
                    route.append(street)
            else:
                route.append(street)
        routes['route'+str(routeCount)] = route
    
    return routes

# Method not currently finished, not currently being used.
# Meant to get coordinates of the path of the route to create a line on a map.
def getRoutesCoords(startCoord: str, endCoord: str) -> dict:
    url = 'https://api.tomtom.com/routing/1/calculateRoute/\
'+startCoord.replace(' ','')+':'+endCoord.replace(' ','')+'/json?\
&instructionsType=text&language=en-US\
&sectionType=traffic\
&report=effectiveSettings\
&routeRepresentation=polyline\
&traffic=true&avoid=unpavedRoads\
&travelMode=car&vehicleMaxSpeed=120\
&vehicleCommercial=false&vehicleEngineType=combustion\
&maxAlternatives=5\
&key=' + API_KEY

    req = urllib.request.urlopen(url)
    routeData = req.read().decode('utf-8')
    routeJSON = json.loads(routeData)

    routes = {}
    route = []
    routeCount=0
    
    routeInstructions = routeJSON['routes']
    print(json.dumps(routeInstructions,indent=4))

    for routeInstruction in routeInstructions[0]['legs']['points']:
        route=[]
        routeCount+=1
        for instruction in routeInstruction:
            print(instruction)
            
            if 'street' not in instruction:
                continue

            street = instruction['street']
            if street in route:
                if route.index(street)!=(len(route)-1):
                    route.append(street)
            else:
                route.append(street)
        routes['route'+str(routeCount)] = route
    
    return routes

def getRoute(startCoord: str, endCoord: str) -> list:
    url = 'https://api.tomtom.com/routing/1/calculateRoute/\
'+startCoord.replace(' ','')+':'+endCoord.replace(' ','')+'/json?\
&instructionsType=text&language=en-US\
&sectionType=traffic\
&report=effectiveSettings\
&routeRepresentation=polyline\
&traffic=true&avoid=unpavedRoads\
&travelMode=car&vehicleMaxSpeed=120\
&vehicleCommercial=false&vehicleEngineType=combustion\
&maxAlternatives=5\
&key=' + API_KEY
    
    req = urllib.request.urlopen(url)
    routeData = req.read().decode('utf-8')
    routeJSON = json.loads(routeData)

    route = []
    instructions = routeJSON['routes'][0]['guidance']['instructions']
    for instruction in instructions:
        if 'street' not in instruction:
            continue

        street = instruction['street']
        if street in route:
            if route.index(street)!=(len(route)-1):
               route.append(street)
        else:
            route.append(street)
    
    return route

def distanceBetweenCoords(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
   '''
   Finds the distance between two coordinates in miles

   Parameters:
   lat1 (float): Latitude of 1st coordinate
   lon1 (float): Longitude of 1st coordinate
   lat2 (float): Latitude of 2nd coordinate
   lon2 (float): Longitude of 2nd coordinate

   Returns:
   float: distance between coordinates (in miles)
   
   '''
   
   dist = math.sqrt(math.pow(lat2-lat1,2)+(math.pow(lon2-lon1,2)))
   distInMiles = dist*69
   return distInMiles

def findZoomLevel(lat1: float, lon1: float, lat2: float, lon2: float) -> int:
   '''
   Finds zoom level of a map snapshot so that both target coordinates are included

   Parameters:
   lat1 (float): Latitude of 1st coordinate
   lon1 (float): Longitude of 1st coordinate
   lat2 (float): Latitude of 2nd coordinate
   lon2 (float): Longitude of 2nd coordinate

   Returns:
   int: Zoom level
   
   '''
   #Figured out using tests of zooms with distances of 1,2,5,10,and 50 miles

   dist = distanceBetweenCoords(lat1,lon1,lat2,lon2)
   if dist<=1:
      return 15
   elif dist<=2:
      return 14
   elif dist<=5:
      return 13
   elif dist<=10:
      return 11
   elif dist<=50:
      return 9
   else:
      return 8
