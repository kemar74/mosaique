from PIL import Image, ImageFilter
import math
import glob
import json
import random
import os, sys
import getopt
import argparse
import decimal

# CMD : python .\mosaique.py palette -v
# CMD : python .\mosaique.py mosaique -v


# Default values :
# - bigPictures 		: images to be splitted into a mosaique
# - smallPicturesDir 	: directory where all little images are stored
# - rgbToFile 			: path to the palette (json) file
# - newImageName		: name of the image after the treatment
# - colorsDistorsion 	: create "noise" on the original image
# - tilesX 				: amount of pictures per row
# - tilesY 				: amount of pictures per column
# - finalSizeX 			: resolution of the image after treatment on the X-axis
# - finalSizeY 			: resolution of the image after treatment on the Y-axis (set as None to keep the original ratio)
# - verbose 			: display text on screen
# - preview 			: display image at the end
# 
# It is possible to create a treatment on more than one photo (bigPictures is an array),
# 	same goes to colorsDistorsion to have different level of distorsion.
# 	So at the end, there will be len(bigPictures)*len(colorsDistorsion) images created
# 	
# Description :
# 	First you need to create the palette from your "small images" directory. 
# 	This is done by executing this command : python .\mosaique.py -dir="path\to\the\small\images\folder" -rgb-file="random_name_of_palette.txt" palette
# 	It will create a file named by "-rgb-file" that contains a hashmap of the type "(R, G, B) => fileOfThePictureCorresponding".
# 	-----------------------
# 	Then you'll be able to launch the main function to transform a picture with the file you have created just before.
# 	Use the command : python .\mosaique -bigPictures=[pic1.png, pic2.png, ...] -dir="path\to\the\small\images\folder" -rgb-file="random_name_of_palette.txt" 
# 						-name="name_of_the_resulting_picture" - colorsDistorsion=[0.20, 0.23, 0.25] -x=nb_tiles_per_row -y=nb_tiles_per_column 
# 						-size-x=final_size_of_the_resulting_picture -verbose -preview=0
# 	
# Global algorithm of the transformation :
# 	- take the original picture and resize it so that one pixel will correspond to one tile (new width = tilesX and new height = tilesY)
# 	- stretch the colors of the picture so that all channels (Red, Green and Blue) has values from 0 to 255
# 	- create an empty image of the desired size (finalSizeX * finalSizeY)
# 	- for each pixel of the reduced original picture, get the color, apply noise (colorsDistorsion) 
# 		so it's not perfectly exact and find the closest color that match in the rgbToFile file
# 	- in the empty image, paste the corresponding image of the color found
# 	- save the image.


bigPictures = ["A:\\Code Perso\\Code Python\\Photos Antoine Menard\\11958129_953136368082684_862721585416868723_o.jpg",
			"A:\\Code Perso\\Code Python\\308732_148493965250001_597912943_n.jpg", 
			"A:\\Code Perso\\Code Python\\423109_223466674419396_106832522_n.jpg", 
			"A:\\Code Perso\\Code Python\\DSC_0896.JPG", 
			"A:\\Code Perso\\Code Python\\IMG-20200109-WA0022.jpg" ]
smallPicturesDir = "A:\\Code Perso\\Code Python\\Photos Antoine Menard"
rgbToFiles = "listImagesAntoine.txt"
newImageName = "patchResult\\patchAntoine40x60.png"
colorsDistortion = frange(0.20, 0.25, 0.05)
tilesX = 40#50
tilesY = 60#75
finalSizeX = 3000
finalSizeY = None
verbose = False
preview = False


# range() with floats
def frange(start, stop, step) :
	ret = []
	i = start
	while i <= stop:
		ret.append(i)
		i = round(step + i, 10) # Need a round for an obscure reason
	return ret

try:   
	# Create the "help" with argparse
	parser=argparse.ArgumentParser(
		description='''Script de transformation d'image vers une mosaique ''')
	parser.add_argument('-picture', '-original', default=bigPictures, 
		help='Image principale à transformer')
	parser.add_argument('-pictures-dir', '-dir', default=smallPicturesDir, 
		help='Dossier contenant les images à utiliser dans la mosaique')
	parser.add_argument('-rgb-file', '-colors', default=rgbToFiles, 
		help='Fichier JSON contenant la palette de couleurs associée à la mosaique')
	parser.add_argument('-new-name', '-name', default=newImageName, 
		help='Nom de l\'image a l\'enregistrement')
	parser.add_argument('-distorsion', '-colors-distorsion', default=colorsDistortion, #[0.3],#frange(0.18, 0.20, 0.01),#0.15, 0.35, 0.010), 
		nargs="*",
		help='Niveau de distorsion entre 0 et 2')
	parser.add_argument('-x', '-tiles-x', type=int, default=tilesX, 
		help='Nombre d\'images à utiliser en largeur')
	parser.add_argument('-y', '-tiles-y', type=int, default=tilesY, 
		help='Nombre d\'images a utiliser en hauteur')
	parser.add_argument('-X', '-size-x', type=int, default=finalSizeX,
		help='Largeur finale de la mosaique (en pixels)')
	parser.add_argument('-Y' '-size-y', type=int, default=finalSizeY, 
		help='Hauteur finale de la mosaique (en pixels)')
	parser.add_argument('-verbose', '-v', nargs="?", type=bool, default=verbose, 
		help='Mode verbal')
	parser.add_argument('-p', '-preview', nargs="?", type=bool, default=preview, 
		help='Affiche les images quand elles sont créées.')
	parser.add_argument("action", default="mosaique", const="mosaique", nargs="?", choices=["mosaique", "palette"], 
		help="Action à réaliser (mosaique ou palette)")
	args = vars(parser.parse_args())

	for opt in args:

		if opt == "picture" :
			bigPictures = args[opt] 
		elif opt == "pictures_dir" :
			smallPicturesDir = args[opt] 
		elif opt == "rgb_file" :
			rgbToFiles = args[opt] 
		elif opt == "new_name" :
			newImageName = args[opt]
		elif opt == "distorsion" :
			colorsDistortion = args[opt] 
		elif opt == "x" :
			tilesX = args[opt] 
		elif opt == "y" :
			tilesY = args[opt] 
		elif opt == "X" :
			finalSizeX = args[opt] 
		elif opt == "Y" :
			finalSizeY = args[opt] 
		elif opt == "verbose":
			verbose = args[opt] or args[opt] == None
		elif opt == "p":
			preview = args[opt] or args[opt] == None

except getopt.GetoptError:          
	usage()                         
	sys.exit(2) 

# Function to create loading bars in the console
# (source : StackOverflow)
progress_x = 0
def startProgress(title):
	global progress_x
	sys.stdout.write(title + ": [" + "-"*40 + "]" + chr(8)*41)
	sys.stdout.flush()
	progress_x = 0

def progress(x):
	global progress_x
	x = int(x * 40 // 100)
	sys.stdout.write("#" * (x - progress_x))
	sys.stdout.flush()
	progress_x = x

def endProgress():
	sys.stdout.write("#" * (40 - progress_x) + "]\n")
	sys.stdout.flush()

# Find the mean color from the image in a rectangle (fromX, toX, fromY, toY)
# "approximation" is used to check less pixels (check 1 out of "approximation" pixels)
# "roundAtEnd" is to know if you want integers or float values
def getMeanColorOfImage(imagePath, fromX=0, toX=None, fromY=0, toY=None, approximation=4, roundAtEnd=False):
	try:
		image = imagePath
		# if imagePath is already a path do nothing, else instanciate the image
		if not isinstance(imagePath, Image.Image):
			image = Image.open(imagePath)
		sums = [0, 0, 0]	# [R, G, B]
		toX = toX if toX else image.width # if toX is not declared, take all the image
		toY = toY if toY else image.height # same for toY
		# for each pixel of the image (but jumping pixels following "approximation")
		for x in range(math.floor(fromX/approximation), math.floor(toX/approximation)):
			for y in range(math.floor(fromY/approximation), math.floor(toY/approximation)):
				r,g,b = image.getpixel((round(x * approximation), round(y * approximation)))	# Get the color and add values to the "sums"
				sums[0] += r
				sums[1] += g
				sums[2] += b
		nbPixels = ((toX-fromX)*(toY - fromY))/(approximation * approximation) # getting the number of pixels scanned
		
		# calculate the mean and round it if needed
		for i in range(len(sums)):
			sums[i] /= nbPixels
			if(roundAtEnd):
				sums[i] = round(sums[i])
		return sums
	except Image.UnidentifiedImageError :
		return False

# Function to create the palette from a directory
def createColorPaletteOfImages(dir):
	if verbose : print("Parcours des fichiers de " + dir)
	# Get all the files in the directory (I don't think it's recursive, didn't check)
	files = glob.glob(dir + "/*.*")
	palette = []
	i = 0
	totalImages = 0
	if verbose : 
		if verbose : print(str(len(files)) + " fichiers trouvés")
		startProgress("Création de la palette de couleurs")

	# For every image found, get the mean color and add it to the "palette" array
	for img in files:
		if verbose : progress(100 * i / len(files))
		color = getMeanColorOfImage(img)
		if(color):
			totalImages += 1
			palette.append((color, img))
		i += 1
	if verbose : endProgress()
	if verbose: print(str(totalImages) + " images trouvées")

	# Return the array containing all the colors found and the image associated
	return palette

# Function to save an object (the palette of colors) as a JSON object
def saveAsJson(obj, name):
	with open(name, "w") as file:
		json.dump(obj, file)

# Function to have only the colors in the palette (ignoring the images associated)
def getAvailableColors(filename):
	with open(filename, "r") as file:
		content = json.load(file)
		colors = []
		# For each line, get only the key (the RGB value)
		for elem in content:
			color = []
			for chanel in elem[0]:
				color.append(round(chanel))
			color = (color[0], color[1], color[2])
			colors.append((color, elem[1]))
		return colors

# Function to stretch all colors from the rgbToFile
# Nothing really intresting : 
# - for each channel (R, G, or B) find the max and the min
# - scale all the values to make the min value = 0 and max value =  255
def stretchColors(colorList):
	minR = minG = minB = 256
	maxR = maxG = maxB = 0
	for elem in colorList:
		color = elem[0]
		if(minR >= color[0]):
			minR = color[0]
		if(minG >= color[1]):
			minG = color[1]
		if(minB >= color[2]):
			minB = color[2]
		if(maxR <= color[0]):
			maxR = color[0]
		if(maxG <= color[1]):
			maxG = color[1]
		if(maxB <= color[2]):
			maxB = color[2]
	for i in range(len(colorList)):
		color = colorList[i][0]
		color = [color[0], color[1], color[2]]
		color[0] -= minR
		color[1] -= minG
		color[2] -= minB

		color[0] *= 256 / (maxR - minR)
		color[1] *= 256 / (maxG - minG)
		color[2] *= 256 / (maxB - minB)

		color[0] = round(color[0])
		color[1] = round(color[1])
		color[2] = round(color[2])

		colorList[i] = (color, colorList[i][1])
	# Return the new colors set
	return colorList


# Function to stretch all colors from an image
# same process, but with an image
def stretchImage(image) :
	minR = minG = minB = 256
	maxR = maxG = maxB = 0

	index = 0
	pixels = list(image.getdata())
	for y in range(image.height) :
		for x in range(image.width) :
			r, g, b = pixels[index]
			if(minR >= r):
				minR = r
			if(minG >= g):
				minG = g
			if(minB >= b):
				minB = b
			if(maxR <= r):
				maxR = r
			if(maxG <= g):
				maxG = g
			if(maxB <= b):
				maxB = b
			index += 1

	index = 0
	for y in range(image.height) :
		for x in range(image.width) :
			r, g, b = pixels[index]
			r -= minR
			g -= minG
			b -= minB

			r *= 256 / (maxR - minR)
			g *= 256 / (maxG - minG)
			b *= 256 / (maxB - minB)

			r = round(r)
			g = round(g)
			b = round(b)

			image.putpixel((x, y), (r, g, b))
			index += 1
	return image

# get a random value from -distModifier to +distModifier 
def randomized(distModifier):
	return (random.random() * distModifier) - (distModifier / 2)
# distore a pixel by +/- distModifier
def distoredColor(color, distModifier) :
	return (color[0] + randomized(distModifier), color[1] + randomized(distModifier), color[2] + randomized(distModifier))

# Function to get the closest color in the palette file
def findClosestColor(color, listColors, returnIndex=False, distorsion=0):
	minDist = -1
	minColor = None
	i = 0
	minIndex = -1
	possibleColors = []
	distored = color # distoredColor(color, distorsion)
	for col in listColors:
		dist = (distored[0] - col[0])**2 + (distored[1] - col[1]) ** 2 + (distored[2] - col[2]) ** 2
		if minDist < 0 or dist < minDist:
			minDist = dist
	for col in listColors:
		dist = (distored[0] - col[0])**2 + (distored[1] - col[1]) ** 2 + (distored[2] - col[2]) ** 2
		if abs(dist - minDist) <= 3*distorsion**2:
			possibleColors.append((i, col))
		i+=1

	minIndex, minColor= random.choice(possibleColors)
	return minColor if not returnIndex else minIndex


def createImageFromSubImages(subImages, originalWidth, originalHeight):
	width = round(originalWidth / len(subImages))
	height = round(originalHeight / len(subImages[0]))
	images = dict() # This is to limit the number of access to the palette file

	if verbose : startProgress("Creation de l'image finale...")
	i = 0
	# Create an empty image
	img = Image.new("RGB", (originalWidth, originalHeight))
	# for all tiles wanted...
	for x in range(len(subImages)):
		for y in range(len(subImages[x])):
			if verbose : progress(100 * i / (len(subImages) * len(subImages[x])))
			if subImages[x][y] not in images:
				images[subImages[x][y]] = Image.open(subImages[x][y]).resize((width, height))
			# Put the image on the "empty" image at the corresponding coordonates
			img.paste(images[subImages[x][y]], (math.floor(x*width), math.floor(y*height)))
			i += 1
	if verbose : endProgress()
	return img


# Create the palette
def saveJsonFile() :
	saveAsJson(createColorPaletteOfImages(smallPicturesDir), rgbToFiles)

# Main function
def createImage(makeDistorsionChange = False):
	if verbose : print("Préparation des couleurs...")
	# stretch the colors of the palette to go from 0 to 255
	elems = stretchColors(getAvailableColors(rgbToFiles))
	justColors = []
	justImages = []
	for e in elems:
		justColors.append(e[0])
		justImages.append(e[1])

	# Do the process for all the "bigPictures" wanted
	for numImg, bigPicture in enumerate(bigPictures) :
		subImages = {}
		if verbose : print("Chargement de l'image d'origine " + str(numImg+1) + " sur " + str(len(bigPictures)) + "...")
		# Open the image
		image = Image.open(bigPicture)
		imgRatio = image.width / image.height
		originalX, originalY = (finalSizeX, math.floor(finalSizeX / imgRatio))
		# Make it smaller so that 1px = 1 tile
		image = image.resize((tilesX, tilesY))
		# stretch the colors so that each channels go from 0 to 255
		image = stretchImage(image)

		if verbose : startProgress("Division de l'image...")
		i = 0
		if not makeDistorsionChange:
			makeDistorsionChange = (colorsDistortion, )

		# for every distorsion level wanted...
		for dist in makeDistorsionChange:
			subImages[str(dist)] = []
			# For each tile...
			for x in range(image.width):
				if verbose : progress(100 * i / (tilesX*tilesY*len(makeDistorsionChange)))
				subImages[str(dist)].append([])
				for y in range(image.height):
					# Find the closest color in the palette (returning the index in the array)
					colIndex = findClosestColor(image.getpixel((x, y)),
											justColors,
											returnIndex = True,
											distorsion = (dist * 255))
					# Use the image corresponding
					subImages[str(dist)][x].append(justImages[colIndex])
					i += 1
		if verbose : endProgress()

		# Save the image (all of this to set the name to : "newName"-"# of bigPicture"_"level of distorsion applied"."extension" )
		maxDecimal = 0
		for dist in makeDistorsionChange:
			maxDecimal = max(maxDecimal, abs(decimal.Decimal(str(dist)).as_tuple().exponent))
		for dist in makeDistorsionChange:
			newImage = createImageFromSubImages(subImages[str(dist)], originalX * 2, originalY * 2)
			name = newImageName.split(".")
			path = "\\".join(newImageName.split("\\")[:-1])
			ext = name[len(name) - 1]
			s_dist = "%.{0}f".format(maxDecimal) % dist
			name.insert(-1, "-" + str(numImg) + "_" + s_dist)
			name = "".join(name[:-1]) + "." + ext
			try:
				os.mkdir(path)
			except FileExistsError:
				pass
			except FileNotFoundError:
				pass
			newImage.save(name)
			if preview :
				newImage.show()


# depending on the action wanted, create the palette or treat images
if(args["action"] == "palette") :
	saveJsonFile()
elif(args["action"] == "mosaique") :
	createImage(colorsDistortion)
else:
	usage()
if verbose : print("Done.")
