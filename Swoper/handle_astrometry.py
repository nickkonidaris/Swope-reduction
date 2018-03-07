import argparse
import astropy
import astropy.io.fits
import glob

import os

astropy.log.setLevel("ERROR")


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument("--glob", default="ccd*.fits", help="glob to include")
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
        exptype = hdr["EXPTYPE"]
        name = hdr["OBJECT"]

        if exptype != "Object":
            print("%s | exposure type: %s skipped." % (file_, exptype))
            continue

        if "bias" in name:
            print("%s | seems to be bias. skipped." % file_)
            continue


        cmd = "solve-field %s --index-xyls %s.xyls --temp-axy --corr %s.corr \
            --match %s.match --rdls %s.rdls --wcs %s.wcs \
            --skip-solved --solved %s.solved --ra %s --dec %s --cpulimit 10 \
            --radius %s --downsample %s --dir %s --new-fits wcs_%s" % \
            (file_, file_, file_, file_, file_, file_, file_, ra, dec, radius, downsample, out, file_)
        print(file_, ra, dec)

        os.system(cmd)
