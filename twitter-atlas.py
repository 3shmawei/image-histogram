import pandas as pd
import numpy as np
import sys
from PIL import Image, ImageDraw
from dateutil import parser
import datetime
import pytz
import os
import glob
from skimage.io import imread
from skimage import color
import time as time_module

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



"""Getting 'secpast' feature"""

df.postedTime = df.postedTime.apply(parser.parse)
df['isoweekday'] = [item.isoweekday() for item in df.postedTime]
df['time'] = [item.time() for item in df.postedTime]
zero = datetime.datetime.combine(datetime.date.today(),datetime.time(0,0,0,0))
secperday = 86400

secpast = []
for w in df.index:

    isoweekday = df.isoweekday.loc[w]
    time = df.time.loc[w]
    dtime = datetime.datetime.combine(datetime.date.today(),time)

    if isoweekday==7:
        secpast.append(int((dtime-zero).total_seconds()))
    else:
        secpast.append(int((dtime-zero).total_seconds()) + (secperday * isoweekday))
    print(i,"secpast",w,"of",len(df))

df['secpast'] = secpast    
df['year'] = [item.year for item in df.postedTime]



# create 'x_bin' column in df using pandas.cut()
df['x_bin'] = pd.cut(df[x_var],num_bins,labels=False)

# find length of largest bin using groupby method
bin_max = df.groupby('x_bin').size().max()

# use bin_max, num_bins, and thumb_side to determine size of canvas
px_w = (thumb_side) * num_bins

# opportunity to game the y-var for oversized histograms
#px_h = px_w
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
    # note 'ascending' kwarg
    tmp = tmp.sort(sort_var,ascending=False)

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
            thumb.thumbnail(thumb_px,Image.ANTIALIAS)
            canvas.paste(thumb,(x_coord,y_coord))
            y_coord = y_coord - thumb_side
        except:
			print 'missing'
print "...done."

print "Saving image..."

# save written canvas to outfile
canvas.save(outfile)

# optional: crop image then save
#top = px_h-px_w
#canvas.crop((0,top,px_w,px_h)).save(outfile.rstrip(".png")+"_cropped.png")

print "...done."
