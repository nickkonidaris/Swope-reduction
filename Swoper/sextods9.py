import argparse
import astropy
import astropy.io.ascii
import numpy as np
astropy.log.setLevel("ERROR")


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("path", default="output.cat", help="file to convert")
    args = parser.parse_args()

    p = args.path

    table = astropy.io.ascii.read(p)

    X = "X_WORLD"
    Y = "Y_WORLD"
    F = "FWHM_WORLD"
    Fl = "FLUX_ISO"
    print("""# Region file format: DS9 version 4.1
global color=green dashlist=8 3 width=1 font="helvetica 10 normal roman" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1
fk5
""")

    for line in table[1:]:
        fwhm = line[F]*3600.
        fl = np.abs(line[Fl]/10)
        print('circle(%s, %s, %s") # color=red' % (line[X], line[Y], np.log10(fl)))
