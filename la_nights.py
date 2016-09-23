import pandas as pd
import numpy as np
import sys
from PIL import Image, ImageDraw

BASE = "/Users/damoncrockett/Desktop/"

x_var = "lat"
sort_var = "hue_mode"
infile = BASE+"lapland/slices_cropped_16/slice_metadata_lat.csv"
outfile = BASE+"lapland/"+x_var+"_"+sort_var+".png"
num_bins = int(sys.argv[1])
thumb_side = int(sys.argv[2])

print "Reading data..."

# read in data file as pandas DataFrame object (df)
df = pd.read_csv(infile)

# option to subset dataframe
df = df[df.sat_median>0.5]
df = df[df.val_median>0.5]

# option to sample the dataframe
df = df.sample(n=204800)

# option to eliminate isnull()
df = df[df[x_var].notnull()]

print "...done."

# create 'x_bin' column in df using pandas.cut()
df['x_bin'] = pd.cut(df[x_var],num_bins,labels=False)

# find length of largest bin using groupby method
bin_max = df.groupby('x_bin').size().max()

# use bin_max, num_bins, and thumb_side to determine size of canvas
px_w = (thumb_side) * num_bins
px_h = (thumb_side) * bin_max
print str(px_w)+'w',str(px_h)+'h'

answer = raw_input("okay?")
if answer == "no":
    exit()
    
# build canvas (final triplet is the color of background, currently dark grey)
canvas = Image.new('RGB',(px_w,px_h),(50,50,50))
# set thumbnail size tuple using thumb_side
thumb_px = (thumb_side,thumb_side)

print "Building image..."

# make a list of unique bins
bins = list(set(list(df.x_bin)))

# build image bin by bin
for item in bins:    	
    # select rows of df in bin
    tmp = df[df.x_bin==item]

    # sort the resulting DataFrame (tmp) by the sorting variable
    tmp = tmp.sort(sort_var)

    # reset index because we'll use the index in a loop
    tmp.reset_index(drop=True,inplace=True)

    # define x and y coordinates for pasting
    y_coord = px_h
    x_coord = thumb_side * item

    # loop over rows in tmp
    n = len(tmp.index)
    for i in range(n):
        try:
            print x_coord,y_coord
            thumb = Image.open(tmp.filename.loc[i])
            #thumb.thumbnail(thumb_px,Image.ANTIALIAS)
            canvas.paste(thumb,(x_coord,y_coord))
            y_coord = y_coord - thumb_side
        except:
            print 'err'
            
print "...done."

print "Saving image..."

# save written canvas to outfile
#canvas.save(outfile)

# optional: crop image then save
m = len(outfile) - 4
top = px_h-px_w*2
canvas.crop((0,top,px_w,px_h)).save(outfile[:m]+"_cropped.png")

print "...done."