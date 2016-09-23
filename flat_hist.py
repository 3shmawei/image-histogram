import pandas as pd
import numpy as np
import sys
from PIL import Image, ImageDraw

infile = sys.argv[1]
num_bins = int(sys.argv[2])
thumb_side = int(sys.argv[3])

print "Reading data..."

# read in data file as pandas DataFrame object (df)
df = pd.read_csv(infile)

# option to sample the dataframe
#df = df.sample(n=1048576)

print "...done."

# This will make num_bins even height bins
m = len(df)
per_bin = int(round(m / num_bins)) + 1
l = np.repeat(range(num_bins),per_bin)
l = l[:m]

x_vars = ['hue_mean','hue_med',
          'sat_mean','sat_med',
          'val_mean','val_med']
          
logos = [
[True,True],
[True,False],
[False,True],
[False,False]
]

for logo in logos:
    for x_var in x_vars:
    
		df.sort(x_var,inplace=True)
		df['x_bin'] = l

		# find length of largest bin using groupby method
		bin_max = df.groupby('x_bin').size().max()

		# use bin_max, num_bins, and thumb_side to determine size of canvas
		px_w = (thumb_side) * num_bins

		# opportunity to game the y-var for oversized histograms
		#px_h = px_w
		px_h = (thumb_side) * bin_max
		print str(px_w)+'w',str(px_h)+'h'

		#answer = raw_input("okay?")
		#if answer == "no":
		#	exit()

		# build canvas (final triplet is the color of background, currently dark grey)
		canvas = Image.new('RGB',(px_w,px_h),(50,50,50))

		# set thumbnail size tuple using thumb_side
		thumb_px = (thumb_side,thumb_side)

		print "Building image..."

		# make a list of unique bins
		bins = list(set(list(df.x_bin)))

		options = [
		['val_mean','hue_mean',[0,.25,.5,.75,1]],
		['val_mean','hue_mean',[0,.25,.75,1]],
		['val_mean','hue_mean',[0,.75,1]],
		['val_mean','hue_mean',[0,.125,.25,.375,.5,.625,.75,.875,1]],
		['val_mean','hue_med',[0,.25,.5,.75,1]],
		['val_mean','hue_med',[0,.25,.75,1]],
		['val_mean','hue_med',[0,.33,.67,1]],
		['val_mean','hue_med',[0,.67,1]],
		['val_mean','hue_med',[0,.75,1]],
		['val_mean','hue_med',[0,.125,.25,.375,.5,.625,.75,.875,1]],
		['val_mean','sat_mean',[0,.25,.5,.75,1]],
		['val_mean','sat_mean',[0,.25,.75,1]],
		['val_mean','sat_mean',[0,.75,1]],
		['val_mean','sat_mean',[0,.125,.25,.375,.5,.625,.75,.875,1]],
		['val_mean','sat_med',[0,.25,.5,.75,1]],
		['val_mean','sat_med',[0,.25,.75,1]],
		['val_mean','sat_med',[0,.33,.67,1]],
		['val_mean','sat_med',[0,.75,1]],
		['val_mean','val_mean',[0,.5,1]]
		]

		for option in options:
			y_bin_var,sort_var,cut = option

			# build image bin by bin
			for item in bins:
				# select rows of df in bin
				tmp = df[df.x_bin==item]
		
				try:
					tmp['y_bin'] = pd.cut(tmp[y_bin_var],cut,labels=False)
				except:
					print "can't bin"
	
				# sort the resulting DataFrame (tmp) by the sorting variable
				# note ascending kwarg

				try:
					#tmp = tmp.sort(['y_bin'],ascending=[False])
					tmp = tmp.sort(['y_bin',sort_var],ascending=logo)
				except:
					print "can't double sort"
					#tmp = tmp.sort(sort_var,ascending=True)
	
				# reset index because we'll use the index in a loop
				tmp.reset_index(drop=True,inplace=True)

				# define x and y coordinates for pasting
				y_coord = px_h
				x_coord = thumb_side * item

				# loop over rows in tmp
				n = len(tmp)
				for i in range(n):
					try:
						print x_coord,y_coord
						thumb = Image.open(tmp.filename.loc[i])
						thumb.thumbnail(thumb_px,Image.ANTIALIAS)
						canvas.paste(thumb,(x_coord,y_coord))
						y_coord = y_coord - thumb_side
					except Exception as e:
						print e
			print "...done."

			print "Saving image..."

			# save written canvas to outfile
			DIR = "/Users/damoncrockett/Desktop/Seoul_selfies/flat_histograms/"
			cutstr = str(cut).translate(None,"][,.")
			logostr = str(logo).translate(None,",")
			outfile = DIR+x_var+"_"+y_bin_var+"_"+sort_var+"_"+str(num_bins)+"_"+cutstr+"_"+logostr+".png"
			canvas.save(outfile)

			# optional: crop image then save
			#top = px_h-px_w
			#canvas.crop((0,top,px_w,px_h)).save(outfile.rstrip(".png")+"_cropped.png")

			print "...done."
