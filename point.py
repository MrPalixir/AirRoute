import sys
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

import math as ma

sys.setrecursionlimit(20000)

im = Image.open('Image/Carte.jpg')

# Correspond au nombre de pixels pour 1 degrés sur l'image
longitudeUn = float(im.size[0] / 360.0)
latitudeUn = float(im.size[1] / 180.0)

# Transforme une longitude donnée en pixel
def calculX(longitude):
    return (longitude * longitudeUn) + (im.size[0] / 2)

# Transforme une latitude donnée en pixel
def calculY(latitude):
    return (im.size[1] / 2) - (latitude * latitudeUn)

# Trace un point de coordonnées (latitude, longitude)
def putPoint(latitude, longitude, nomVille) :

    x = calculX(longitude)
    y = calculY(latitude)
 
    font = ImageFont.truetype("Fonts/times-new-roman.ttf", 25)
    draw = ImageDraw.Draw(im)
    draw.text((x - 15, y), nomVille, (255, 0, 0), font=font)
    
    for i in range (-2, 2) :
        for j in range (-2, 2):
            im.putpixel((int(x + i), int(y + j)), (255, 0, 0))
         
# Calcul la distance orthodromique entre 2 points
def calculOrthodromique(latitudeA, longitudeA, latitudeB, longitudeB):
    latitudeA = ma.radians(latitudeA)
    longitudeA = ma.radians(longitudeA)
    latitudeB = ma.radians(latitudeB)
    longitudeB = ma.radians(longitudeB)
    
    B = ma.acos(ma.sin(latitudeA) * ma.sin(latitudeB) + ma.cos(latitudeA) * ma.cos(latitudeB) * ma.cos(longitudeA - longitudeB))

    return B * 6371

# Calcul la distance loxodromique entre 2 points
def calculLoxodromique(latitudeA, longitudeA, latitudeB, longitudeB):
    cap = calculCapConstant(latitudeA, longitudeA, latitudeB, longitudeB)

    B = (ma.radians(latitudeB - latitudeA)) / ma.cos(ma.radians(cap)) 
    
    return B * 6371

# Calcul le cap initiale entre 2 points, on l'utilise pour le calcul des routes orthodromiques
def calculCapInitiale(latitudeA, longitudeA, latitudeB, longitudeB):
    latitudeA = ma.radians(latitudeA)
    longitudeA = ma.radians(longitudeA)
    latitudeB = ma.radians(latitudeB)
    longitudeB = ma.radians(longitudeB)
    
    B = ma.acos(ma.sin(latitudeA) * ma.sin(latitudeB) + ma.cos(latitudeA) * ma.cos(latitudeB) * ma.cos(longitudeA - longitudeB))

    V = (ma.sin(latitudeB) - ma.sin(latitudeA) * ma.cos(B)) / (ma.cos(latitudeA) * ma.sin(B))
    
    if(longitudeA < longitudeB) and (ma.fabs(longitudeA - longitudeB) < ma.pi):
        return ma.degrees(ma.acos(V))
    
    if(longitudeA > longitudeB) and (ma.fabs(longitudeA - longitudeB) < ma.pi):
        return ma.degrees(2 * ma.pi - ma.acos(V))
    
    if(longitudeA < longitudeB) and (ma.fabs(longitudeA - longitudeB) >= ma.pi):
        return ma.degrees(2 * ma.pi - ma.acos(V))
    
    if(longitudeA > longitudeB) and (ma.fabs(longitudeA - longitudeB) >+ ma.pi):
        return ma.degrees(ma.acos(V))
    
    if(ma.fabs(longitudeA - longitudeB) < ma.pow(10, -8)):
        return ma.degrees(0)

# Calcul le cap constant, , on l'utilise pour le calcul des routes loxodromiques
def calculCapConstant(latitudeA, longitudeA, latitudeB, longitudeB):
    latitudeA = ma.radians(latitudeA)
    longitudeA = ma.radians(longitudeA)
    latitudeB = ma.radians(latitudeB)
    longitudeB = ma.radians(longitudeB)
    
    V = ma.atan((longitudeB - longitudeA) / ((ma.log(ma.tan(latitudeB / 2.0 + ma.pi / 4.0))) - ma.log(ma.tan(latitudeA / 2.0 + ma.pi / 4.0))))
    
    return ma.degrees(V) - 180 

# Transforme des degrés en distance
def calculDegreesForDistance(l):
    perimetre = 2.0 * ma.pi * (6371.0 * ma.cos(0))
    
    distance = (l * 360) / perimetre
    
    return distance

# Transforme une distance en degrés
def calculDistanceForDegrees(alpha):
    perimetre = 2.0 * ma.pi * (6371.0 * ma.cos(0))
    
    degrees = (alpha * perimetre) / 360
    
    return degrees

# Trace la route loxodromique
def calculPointSuivantLoxodromie(latitudeA, longitudeA, latitudeC, longitudeC, z):    
    xA = calculX(longitudeA)
    yA = calculY(latitudeA)
    xB = calculX(longitudeC)
    yB = calculY(latitudeC)
    pente = (yB - yA) / (xB - xA)
    b = yA - (pente * xA)
    
    for i in range(100):
        if (ma.sqrt(ma.pow((xA - 10 * i) - (xB), 2) + ma.pow((pente * (xA - 10 * i) + b) - (yB), 2))) < 10.0:
            return
        
        for k in range (-2, 2) :
            for j in range (-2, 2):
                im.putpixel((int((xA - 10 * i) + k), int((pente * (xA - 10 * i) + b)) + j), (255, 0, 0))

# Trace la route orthodromique entre 2 points
def calculPointSuivant(cap, l, latitudeA, longitudeA, latitudeB, longitudeB, latitudeC, longitudeC, z) :    
    cap = calculCapInitiale(latitudeB, longitudeB, latitudeC, longitudeC)
    
    longueurX = l * ma.sin(ma.radians(cap))
    longueurY = l * ma.cos(ma.radians(cap))
    
    longi = calculDegreesForDistance(longueurX)
    lat = calculDegreesForDistance(longueurY)

    # On vérifie si la route ne dépasse pas de l'image au pôle nord
    if calculY(latitudeB + lat) <= 5:
        if z >= 1:
            return
        
        calculPointSuivant(0, l, latitudeC, longitudeC, latitudeC, longitudeC, latitudeA, longitudeA, 1)
        return
    
    # On vérifie si la route ne dépasse pas de l'image au pôle sud
    if calculY(latitudeB + lat) >= 1020:
        if z >= 1:
            return
        
        calculPointSuivant(0, l, latitudeC, longitudeC, latitudeC, longitudeC, latitudeA, longitudeA, 1)
        return
    
    # On vérifie si la route ne dépasse pas de l'image à l'est
    if calculX(longitudeB + longi) >= calculX(179):
        putPoint(latitudeB + lat, -179, '')
        calculPointSuivant(0, l, latitudeA, longitudeA, latitudeB + lat, -179, latitudeC, longitudeC, z)
        return
    
    # On vérifie si la route ne dépasse pas de l'image à l'ouest
    if(calculX(longitudeB + longi) <= calculX(-179)):
        putPoint(latitudeB + lat, 179, '')
        calculPointSuivant(0, l, latitudeA, longitudeA, latitudeB + lat, 179, latitudeC, longitudeC, z)
        return

    ecartEnKmLongitude = calculDistanceForDegrees(ma.fabs(longitudeC - longitudeB))
    ecartEnKmLatitude = calculDistanceForDegrees(ma.fabs(latitudeC - latitudeB))
    
    # On vérifie si la distance restante entre le point courant et le point final est inférieur à la longueur d'un tronçon
    if (ma.sqrt(ma.pow(ecartEnKmLongitude, 2) + ma.pow(ecartEnKmLatitude, 2))) < l:
        return
    
    # On affiche un point sur la carte
    putPoint(latitudeB + lat, longitudeB + longi, '')
    
    # Appel récursif
    calculPointSuivant(cap, l, latitudeA, longitudeA, latitudeB + lat, longitudeB + longi, latitudeC, longitudeC, z)
  
# ----------------------------------------------------------------------------------------------

# On affiche les différentes villes
putPoint(48.87, 2.33, 'Paris')
putPoint(35.69, 139.69, 'Tokyo')
putPoint(-33.55, 18.25, 'Le Cap')
putPoint(19.43, -99.1, 'Mexico')
putPoint(-53.1, -70.9, 'Punta Arenas')
putPoint(34.05, -118.24, 'Los Angeles')
#putPoint(40.43, -74, 'New-York')


# On affiche 2 routes orthodromiques
calculPointSuivant(0, 10, -77.5, -52.3, -77.5, -52.3, -76.5, 97.6, 0)
calculPointSuivant(0, 10, 77.5, 52.3, 77.5, 52.3, 76.5, -97.6, 0)
#calculPointSuivant(0, 10, 35.69, 139.69, 35.69, 139.69, 34.05, -118.24, 0)

#lat1 = float(input("Veuillez rentrez une latitude de départ : "))
#lon1 = float(input("Veuillez rentrez une longitude de départ : "))
#
#lat2 = float(input("Veuillez rentrez une latitude de fin : "))
#lon2 = float(input("Veuillez rentrez une longitude de fin : "))

#calculPointSuivant(0, 10, lat1, lon1, lat1, lon1, lat2, lon2, 0)
#calculPointSuivant(0, 10, lat1, lon1, lat1, lon1, lat2, lon2, 0)

im.show()