import argparse
import astropy
import astroalign as aa
import astropy.io.fits

import os
import numpy as np

astropy.log.setLevel("ERROR")


if __name__ == '__main__':

    import sys

    source = sys.argv[1]
    rest = sys.argv[2:]
    print("Mapping %s to %s" % (source, rest))

    hdu = astropy.io.fits.open(source)
    dat = hdu[0].data

    for fname in rest:
        hdu = astropy.io.fits.open(fname)
        d2 = hdu[0].data

        new = aa.register(dat, d2)

        hdu = astropy.io.fits.PrimaryHDU(new)
        outname = "reg_%s" % fname
        print("Writing to : %s" % outname)
        hdu.writeto(outname)






