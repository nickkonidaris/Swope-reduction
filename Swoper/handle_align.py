import argparse
import astropy
import astroalign as aa
import astropy.io.fits

import os
import numpy as np

astropy.log.setLevel("ERROR")


if __name__ == '__main__':

    import sys

    source = sys.argv[2]
    rest = sys.argv[3:]
    print("Mapping all to %s" % source)

    hdu = astropy.io.fits.open(source)
    dat = hdu[0].data
    print(dat)


    for fname in rest:
        print(fname)
        hdu = astropy.io.fits.open(fname)
        d2 = hdu[0].data

        new = aa.register(dat, d2)

        hdu = astropy.io.fits.PrimaryHDU(new)
        hdu.writeto("reg_%s" % fname)






