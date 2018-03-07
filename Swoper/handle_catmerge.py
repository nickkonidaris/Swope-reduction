import argparse
import astropy
import astropy.io.fits
import ccdproc
import progressbar

import glob
import os
import string
import numpy as np

from ccdproc import ImageFileCollection
import astropy.units as u

import matplotlib as mpl
mpl.use('Agg')
import pylab as pl

astropy.log.setLevel("ERROR")

if __name__ == '__main__':

    header_values = ["FNAME", "AIRMASS", "UT-TIME", "EXPTIME", "FILTER",
                     "TEMPCCD"]

    for c in ["c1", "c2", "c3", "c4"]:
        fs = glob.glob("rp*%s*fits" % c)

        results = None
        meta = None
        # results[object#]["KEY"] -> (array of length # observations)
        bar = progressbar.ProgressBar(max_value=len(fs))
        for ix, fname in enumerate(fs):
            dat = astropy.io.fits.open(fname)
            tab = dat[2].data
            fitsname = "../" + fname.replace(".cat.fits", "")

            if ix == 0:
                results = []
                metares = {}
                keys = [el.name for el in tab.columns]

                for k in header_values:
                    metares[k] = np.chararray(len(fs), 30)
                    metares[k][:] = ""


            hdr = astropy.io.fits.getheader(fitsname)
            for k in header_values:
                if k == "FNAME":
                    metares[k][ix] = fitsname
                else:
                    metares[k][ix] = hdr[k]

            results.append(tab)

            bar.update(ix)

        results = np.array(results)

        np.save("%s_results.npy" % c, [metares, results])


