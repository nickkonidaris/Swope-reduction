import argparse
import astropy
import astropy.io.fits
import glob

import os

astropy.log.setLevel("ERROR")


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument("--glob", default="*.fits", help="glob to include")
    parser.add_argument("--radius", default="1", help="Radius to search around")
    parser.add_argument("--downsample", default="1", help="Number of pixels to \
                        downsample the image by.")
    parser.add_argument("--outdir", default="solved", help="Output directory \
                        name")

    args = parser.parse_args()

    radius = args.radius
    downsample = args.downsample
    files = glob.glob(args.glob)
    out = args.outdir

    try: os.mkdir(out)
    except FileExistsError: pass


    for file_ in files:
        hdr = astropy.io.fits.getheader(file_)
        ra = hdr["RA"]
        dec = hdr["DEC"]
        cmd = "solve-field %s --index-xyls none --axy none --corr none \
            --match none --rdls none --wcs none \
            --skip-solved --overwrite --ra %s --dec %s \
            --radius %s --downsample %s --dir %s --new-fits wcs_%s" % \
            (file_, ra, dec, radius, downsample, out, file_)
        print(file_, ra, dec)

        os.system(cmd)
