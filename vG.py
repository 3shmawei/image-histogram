import pandas as pd
import numpy as np
import sys
from PIL import Image

DIR = "/Users/damoncrockett/Desktop/van_Gogh/"
df = pd.read_csv(DIR+"slices/slice_metadata_cats.csv")

cats = ['Season']
        #'Label_Place','Year','Season']

thumb_side = 8
x_var = "sat"
sort_var = "hue"
num_bins = 720

for cat in cats:
    vals = list(set(list(df[cat])))
    for val in vals:
        subset = df[df[cat]==val]
        
        try:
            subset = subset.sample(n=2048*117)
            #subset = df.sample(n=2048*3)
        except:
            pass
            
        outfile = DIR + cat + "_" + str(val) + ".png"
        #outfile = DIR + "overall.png"
    
        subset['x_bin'] = pd.cut(subset[x_var],num_bins,labels=False)
        bin_max = subset.groupby('x_bin').size().max()
        pad = 0
        px_w = (thumb_side + 2 * pad) * num_bins
        px_h = (thumb_side + pad * 2) * bin_max

        canvas = Image.new('RGB',(px_w,px_h),(50,50,50))

        thumb_px = (thumb_side,thumb_side)

        bins = list(set(list(subset.x_bin)))
        bins.pop(0) # to remove lowest sat bin; too tall

        for item in bins:
            tmp = subset[subset.x_bin==item]
            tmp = tmp.sort(sort_var,ascending=True)
            tmp.reset_index(drop=True,inplace=True)

            y_coord = px_h - (thumb_side + pad)
            x_coord = ((thumb_side + pad) * item) + pad

            n = len(tmp.index)
            for i in range(n):
                print x_coord,y_coord
                thumb = Image.open(tmp.filename.loc[i])
                thumb.thumbnail(thumb_px,Image.ANTIALIAS)
                canvas.paste(thumb,(x_coord,y_coord))
                y_coord = y_coord - (thumb_side + pad)

        canvas.save(outfile)