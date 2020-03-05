# mosaique
Split an image into lots of little ones


## Classic use in command-line (using default values in the source code):
Run once :
```console
python .\mosaique.py palette -v
```
then 
```console
python .\mosaique.py mosaique -v
```

## Command-line
Run once :
```console
python .\mosaique.py -dir="path\to\the\small\images\folder" -rgb-file="random_name_of_palette.txt" palette
```
then
```console
python .\mosaique -bigPictures=[pic1.png, pic2.png, ...] -dir="path\to\the\small\images\folder" -rgb-file="random_name_of_palette.txt" -name="name_of_the_resulting_picture" - colorsDistorsion=[0.20, 0.23, 0.25] -x=nb_tiles_per_row -y=nb_tiles_per_column -size-x=final_size_of_the_resulting_picture -verbose -preview=0
```

## Details
It is possible to create a treatment on more than one photo (bigPictures is an array),
	same goes to colorsDistorsion to have different level of distorsion.
	So at the end, there will be len(bigPictures) \times len(colorsDistorsion) images created
 	
## Description 
First you need to create the palette from your "small images" directory.  
This is done by executing this command : ```python .\mosaique.py -dir="path\to\the\small\images\folder" -rgb-file="random_name_of_palette.txt" palette```  
It will create a file named by "-rgb-file" that contains a hashmap of the type "(R, G, B) => fileOfThePictureCorresponding".

-----------------------

Then you'll be able to launch the main function to transform a picture with the file you have created just before.  
Use the command : ```python .\mosaique -bigPictures=[pic1.png, pic2.png, ...] -dir="path\to\the\small\images\folder" -rgb-file="random_name_of_palette.txt" -name="name_of_the_resulting_picture" - colorsDistorsion=[0.20, 0.23, 0.25] -x=nb_tiles_per_row -y=nb_tiles_per_column -size-x=final_size_of_the_resulting_picture -verbose -preview=0```
 	
## Global algorithm of the transformation
* take the original picture and resize it so that one pixel will correspond to one tile (new width = tilesX and new height = tilesY)
* stretch the colors of the picture so that all channels (Red, Green and Blue) has values from 0 to 255
* create an empty image of the desired size (finalSizeX * finalSizeY)
* for each pixel of the reduced original picture, get the color, apply noise (colorsDistorsion) so it's not perfectly exact and find the closest color that match in the rgbToFile file
* in the empty image, paste the corresponding image of the color found
* save the image.
 
