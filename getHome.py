import os
import copy
from cfonts import render
import configparser

from tomtom import structuredGeocode
from tomtom import reverseGeocode
from tomtom import getRoutes
from tomtom import findZoomLevel
from tomtom import createFoliumMap
from tomtom import createNewAddress
from tomtom import findRandomCoords

output = render('GET HOME', colors=['red', 'yellow'], align='left')
print(output)

# Create "Maps" folder if it doesn't exist.
if not os.path.exists("Maps"):
    os.makedirs("Maps")
    
# Check if API Key exists
Config = configparser.ConfigParser()
Config.read("config.ini")
if Config.get('TomTom', 'API_KEY')=='':
    print("No TomTom API key detected. Please input API key into config.ini and try again.")
    quit()
    
print("To begin, please input a starting address below (this can be changed later): ")
resp = createNewAddress()
print('')

def game():
    #Get coordinates from address
    structuredGeocodingJSON = structuredGeocode(resp)

    #save address and coords
    address = structuredGeocodingJSON['results'][0]['address']['freeformAddress']
    structuredCoords = structuredGeocodingJSON['results'][0]['position']

    #Choosing, calculating difficulty
    latitude = structuredCoords['lat']
    longitude = structuredCoords['lon']
    fullHomeCoords = str(latitude)+', '+str(longitude)

    print('')
    difficulty = input("Select a difficulty (1-5)\n1 - 1 mile radius\n2 - 2.5 mile radius\n3 - 5 mile radius\n4 - 10 mile radius\n5 - 50 mile radius\nInput choice here: ")
    diffDict = {'1': 1, '2': 2.5, '3': 5, '4': 10, '5': 50}
    radius = diffDict.get(difficulty)
    print('')
    randCoords = findRandomCoords((latitude, longitude), difficulty)
    fullRandCoords = str(randCoords[0])+', '+str(randCoords[1])
    randAddress = reverseGeocode(str(randCoords[0]), str(randCoords[1]))

    print('-------------------------------------------------------------------------------------------------------------------------------------------------------------')
    print("The random location within a " + str(radius) + " mile radius is: " + randAddress + " with coordinates of (" + str(randCoords[0])+','+str(randCoords[1]) + ")")
    print('-------------------------------------------------------------------------------------------------------------------------------------------------------------')

    routes: dict = getRoutes(fullRandCoords,fullHomeCoords)
    routesCopy = copy.deepcopy(routes)

    zoomLevel = findZoomLevel(latitude,longitude,randCoords[0],randCoords[1])
    #getStillSnap(str(centerXCoord), str(centerYCoord), zoomLevel, '('+str(radius)+')-' +randAddress+ '-' +address)
    createFoliumMap(address, (latitude,longitude), randAddress, (randCoords[0], randCoords[1]), zoomLevel)

    print("Good luck getting home! ")
    print('')
    print("You begin with 3 lives")

    # User begins guessing the streets in order
    lives = 3

    #Making all the streets lowercase
    for route in routes.values():
        for street in route:
            route[route.index(street)] = street.lower()


    '''
    Explanation of how to keep track of which path user is taking:

    Everytime a user guesses, we will iterate through our routes to see if the user's current route matches up to any available routes so far
    If any routes match up, we can call that a correct guess.
    If no routes match up, then that is an incorrect guess.

    With each correct guess, we eliminate any other routes that do not match up with the user's current path (account for route length)

    If the player guesses all the way to home, this means that they have matched one and ONLY one route because all other routes will have been deleted
    
    '''
    userRoute = []
    currStreetIndex = 0
    routeExactMatch = False
    routeExactMatchName = ''
    numNotMatches=0
    routesNotMatched = []

    while lives>0 and routeExactMatch==False:
        print('-----------------------------------------')
        #Reset these values each guess:
        numNotMatches=0
        routesNotMatched=[]

        user_guess = input("Please input a street to get home: ").lower()

        #If user tries to cheat by inputting st or ave
        if (user_guess == 'st' or user_guess == 'ave' or user_guess == "interstate" or user_guess == "highway" or user_guess == "freeway"):
            print("Please guess an actual street...\n")
            continue

        userRoute.append(user_guess)

        #For every route...
        for routeName,route in routes.items():
            #Check if userRoute doesn't match up with route
            for i in range(0,len(userRoute)):
                if userRoute[i] not in route[i]:
                    numNotMatches+=1
                    routesNotMatched.append(routeName)
        
        #If no routes match up, then that is an incorrect guess.
        if numNotMatches==len(routes):
            lives-=1
            print("Incorrect.")
            if lives!=0:
                print("Try this street again. (" + str(lives) + " lives remaining)")

            #Get rid of current guess from userRoute so that we DONT keep track of incorrect guesses
            userRoute.pop()

            continue

        else:   # There was at least one route that matched up
            print("Correct. (" + str(lives) + " lives remaining)")
            currStreetIndex+=1

            #Only delete invalid routes when user guesses correctly
            for name in routesNotMatched:
                del routes[name]

        #Check for a win

        if len(routes)==1 and (len(userRoute)==len(routes[list(routes)[0]])):
            #Check if both routes have same values
            for i in range(0, len(userRoute)):
                if userRoute[i] not in routes[list(routes)[0]][i]:
                    break
            #If everything is matching, then routeExactMatch=True
            routeExactMatch=True
            routeExactMatchName = list(routes)[0]
        

    if routeExactMatch==True:  #User wins
        print('|---------------------------------|')
        print("|           You win!              |")
        print('|---------------------------------|')
    else:
        print('|---------------------------------|')
        print("|           You lose!             |")
        print('|---------------------------------|')

    #Print correct route, display route on maps
    print('')
    print("Your guessed route: " + str(userRoute))

    #Print best route
    # Default to the best route being route1, unless routes is not empty
    if lives==0:  # If the user couldn't guess correctly
        print("A correct route: " + str(routesCopy['route1']))
    else:  # If the user guessed a path correctly, find another path besides the one they chose
        for routeName in routesCopy.keys():
            if routeName != routeExactMatchName:
                print("Another alternative is: " + str(routesCopy[routeName]))
                break

print('|---------------------------------|')
print("|       Starting new game...      |")
print('|---------------------------------|')
print('')

game()

playAgain = True
while playAgain==True:
    print('')
    print('')
    playAgainInput = input("Would you like to play again? (y/n): ")
    if (playAgainInput=='y'):
        #Generate new home, create new route, pretty much do everything again
        switchHouseInput = input("Would you like to change your address? (y/n): ")
        if (switchHouseInput=='y'):
            print("Got it. Please fill out the address form below:")
            resp=createNewAddress()
        game()
    elif (playAgainInput=='n'):
        print("\nThank you for playing! Have a great day!")
        playAgain=False