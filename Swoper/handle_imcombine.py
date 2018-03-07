import argparse
import astropy
import astropy.io.fits
import ccdproc

import os
from ccdproc import ImageFileCollection
from ccdproc import wcs_project

astropy.log.setLevel("ERROR")


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default=".", help="glob to exclude")
    args = parser.parse_args()

    for channel in ["c1", "c2", "c3", "c4"]:
        ic = ImageFileCollection(args.path, glob_include="wcs*%s*fits" % \
                                 channel)
        first = None
        reprojected = []
        for img, fname in ic.ccds(return_fname=True):
            if first is None:
                first = img
                print("New")
                reprojected.append(first)
                os.system("cp %s rp_%s" % (fname, fname))
                continue

            print(fname)

            new = wcs_project(img, first.wcs) #, order="nearest-neighbor")
            try: new.write("rp_%s" % fname)
            except OSError: continue
            reprojected.append(new)

        combiner = ccdproc.Combiner(reprojected)
        stacked_image = combiner.average_combine()
        first.data = stacked_image.data
        try: first.write("%s_stack.fits" % channel)
        except OSError: continue

