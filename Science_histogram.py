# created May 2015 by Cherie M Huang
# modified July 2015 by Damon Crockett

import pandas as pd
import numpy as np
import sys
from PIL import Image

"""
This code uses the Python Image Library to build a histogram of images. You should prepare
your data as follows:

0. Put all your images into one folder
1. In your data file, make a column of file paths that point to the images in this folder,
   call it 'filename'
2. Choose your x variable
3. Choose a number of bins for your x-variable
4. Choose a sorting variable for the y-axis (not really a histogram thing, but adds
   another sorted dimension)
5. Choose a thumbnail size

In terminal window, type:

$ python learning.py <data file> <outfile> <x var> <sorting var> <bins> <thumb size>

Here's an example:

$ python learning.py ./data.csv ./img.png lon hue 20 100
"""

infile = sys.argv[1]
outfile = sys.argv[2]
x_var = sys.argv[3]
sort_var = sys.argv[4]
num_bins = int(sys.argv[5])
thumb_side = int(sys.argv[6])

print "Reading data..."

# read in data file as pandas DataFrame object (df)
df = pd.read_csv(infile)

# option to sample the dataframe
#df = df.sample(n=1048576)

print "...done."

# create 'x_bin' column in df using pandas.cut()
df['x_bin'] = pd.cut(df[x_var],num_bins,labels=False)

# find length of largest bin using groupby method
bin_max = df.groupby('x_bin').size().max()

# use bin_max, num_bins, and thumb_side to determine size of canvas
pad = 0
px_w = (thumb_side + 2 * pad) * num_bins

# opportunity to game the y-var for oversized histograms
#px_h = 3344
px_h = (thumb_side + pad * 2) * bin_max
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
bins.pop(0)

# build image bin by bin
for item in bins:
    # select rows of df in bin
    tmp = df[df.x_bin==item]
    
    # 'puresort' to bind identicals
    #puresortvar = "hue_mode"
    #tmp = tmp.sort([puresortvar])
    # option to double sort, need to bin first
    #y_bin_var = 'val_mean'
    #try:
        #tmp['y_bin'] = pd.cut(tmp[y_bin_var],[0,.5,1],labels=False)
    #except:
        #print "can't bin"
    # sort the resulting DataFrame (tmp) by the sorting variable
    # note ascending kwarg
    #try:
        #tmp = tmp.sort(['y_bin'],ascending=[False])
        #tmp = tmp.sort(['y_bin',sort_var],ascending=[True,True])
    #except:
        #tmp = tmp.sort(sort_var,ascending=True)
        
    tmp = tmp.sort(sort_var,ascending=True)
    # reset index because we'll use the index in a loop
    tmp.reset_index(drop=True,inplace=True)

    # define x and y coordinates for pasting
    y_coord = px_h - (thumb_side + pad)
    x_coord = ((thumb_side + pad) * item) + pad

    # loop over rows in tmp
    n = len(tmp.index)
    for i in range(n):
        print x_coord,y_coord
        thumb = Image.open(tmp.filename.loc[i])
        thumb.thumbnail(thumb_px,Image.ANTIALIAS)
        canvas.paste(thumb,(x_coord,y_coord))
        y_coord = y_coord - (thumb_side + pad)

print "...done."

print "Saving image..."

# save written canvas to outfile
canvas.save(outfile)

# optional: crop image then save
#top = px_h-px_w
#canvas.crop((0,top,px_w,px_h)).save(outfile.rstrip(".png")+"_cropped.png")

print "...done."
