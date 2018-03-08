""" Handle bias, overscan, dark, and flats (BODF) for Swope 4-channel CCD

(c) Nicholas P Konidaris II

See LICENSE for details

"""

import argparse
import astropy
import astropy.io.fits
import ccdproc

import os
import string
import numpy as np

from ccdproc import ImageFileCollection
import astropy.units as u

import matplotlib as mpl
mpl.use('Agg')
import pylab as pl

astropy.log.setLevel("ERROR")


def format_filename(s):
    """Take a string and return a valid filename constructed from the string.
Uses a whitelist approach: any characters not present in valid_chars are
removed. Also spaces are replaced with underscores.

Note: this method may produce invalid filenames such as ``, `.` or `..`
When I use this method I prepend a date string like '2009_01_15_19_46_32_'
and append a file extension like '.txt', so I avoid the potential of using
an invalid filename.

Taken from a gist

"""
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in s if c in valid_chars)
    filename = filename.replace(' ', '_')
    return filename


def mkdir_nowarn(path):
    try:
        os.makedirs(path)
    except FileExistsError:
        pass


def collect_set(ic, collect_by, trim="[2:2047,2:2055]",
                bias={1: None, 2: None, 3: None, 4: None},
                dark={1: None, 2: None, 3: None, 4: None},
                flat={1: None, 2: None, 3: None, 4: None},
                gain_corrected=False, dark_exposure_time=None,
                CRR=False, **kwargs):
    """ Organize an image collection to a dict of lists of CCD by amplifier.

    Searches through ic to find files that have keywords indicated by
    `collect_by`, for each amplifier it creates a list of CCDs that match the
    aforementioned criteria.

    It returns a dictionary {opamp number -> [list of CCD objects]} with the
    collected objects organized.

    Args:
            collect_by: dictionary of {header keyword -> desired header value}
            ic: ImageCollection class

    Example:
        path = "/path/to/files"
        ic = ImageFileCollection(path)
        col = collect_set(ic, {"filter": "u", "exptype": "bias"})
    """

    ccdargs = {"unit": "adu"}

    peramp = {1: [], 2: [], 3: [], 4: []}

    print("Handling: %s" % collect_by)
    for fname in ic.files_filtered(**collect_by):

        print(fname)
        try:
            ccd = astropy.nddata.CCDData.read(fname, **ccdargs)
        except Exception:
            print ("I DON'T LIKE THIS")
            continue

        dat = ccdproc.subtract_overscan(ccd, overscan=ccd[:, 2049:], **kwargs)
        dat = ccdproc.trim_image(dat, fits_section=dat.header["TRIMSEC"])
        dat = ccdproc.create_deviation(dat, gain=dat.header["EGAIN"] *
                                       u.electron/u.adu, readnoise=
                                       ccd.header["ENOISE"]*u.electron)
        dat = ccdproc.gain_correct(dat, gain=ccd.header["EGAIN"] *
                                   u.electron/u.adu)
        AMP = dat.header["OPAMP"]
        if bias[AMP] is not None:
            dat = ccdproc.subtract_bias(dat, bias[AMP])
        if dark[AMP] is not None:
            dat = ccdproc.subtract_dark(dat, dark[AMP])
            # TODO: Scale exposure times
        if flat[AMP] is not None:
            dat = ccdproc.flat_correct(dat, flat[AMP])
        if CRR:
            dat = ccdproc.cosmicray_lacosmic(dat, sigclip=5, psffwhm=3.2)



        peramp[AMP].append(dat)

        """
        dat = ccdproc.ccd_process(ccd, oscan=ccd[:, 2049:],
                                  trim="[2:2047,2:2055]", error=True,
                                  master_bias=bias[ccd.header["OPAMP"]],
                                  dark_frame=dark[ccd.header["OPAMP"]],
                                  dark_exposure=dark_exposure_time,
                                  master_flat=flat[ccd.header["OPAMP"]],
                                  gain_corrected=gain_corrected,
                                  gain=ccd.header["EGAIN"]*u.electron/u.adu,
                                  readnoise=ccd.header["ENOISE"]*u.electron)
        """

    return peramp


def combine_collection(peramp, combine='median', diagnostic=False):
    """ Takes a set from collect_set and combines items for each amplifier. """
    combined = {}

    for opamp, ccds in peramp.items():
        if len(ccds) == 0:
            print("Nothing to combine for %s" % opamp)
            return combined

        print("Combining %s" % opamp)

        if combine == 'average':
            mb = ccdproc.Combiner(ccds, dtype=np.float64).average_combine()
        elif combine == 'median':
            mb = ccdproc.Combiner(ccds, dtype=np.float64).median_combine()
        combined[opamp] = mb

        if diagnostic:
            if opamp == 1:
                running = ccds[0].data.copy()
                roi = (slice(800, 900), slice(800, 900))
                sds = []
                for i, ccd in enumerate(ccds[1:]):
                    sds.append(np.std(running[roi]/(i+1)))
                    running += ccds[i].data
                v = np.arange(len(sds))+1

                pl.figure(1)
                pl.clf()
                pl.plot(v, sds, 'o')
                pl.xlabel("# obs")
                pl.ylabel("SD")

                tn = sds[0]
                bn = tn/7
                rn = np.sqrt(tn**2-bn**2)

                noise = np.sqrt((rn/np.sqrt(v))**2 + bn**2)
                pl.title("RN: %2.1f, Bias Noise: %2.1f" % (rn, bn))
                pl.plot(v, noise)
                pl.legend(["Meas", "Model"])

    return combined


def write_collection(collection, outdir="OUT/", name="out"):
    print("writing collection")
    for amp, images in collection.items():
        print("To path %s" % outdir)
        mkdir_nowarn(outdir)


        for image in images:
            fname = "%s/%s_proc.fits" % (outdir, image.header["filename"])
            print("To: %s" % fname)
            try: os.remove(fname)
            except FileNotFoundError: pass
            image.write(fname)


def write_comb(comb, name="out"):

    for k, ccd in comb.items():
        fname = "OUT/%s_%s.fits" % (format_filename(name), k)
        try:
            os.remove(fname)
        except FileNotFoundError:
            pass
        ccd.write(fname)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument("--include", default=None, help="glob to include")
    parser.add_argument("--exclude", default=None, help="glob to exclude")
    parser.add_argument("--path", default=".", help="glob to exclude")
    parser.add_argument("--verbose", default=False, help="glob to exclude")
    parser.add_argument("--flatname", default="Quartz dome flat - 900 V",
                        help="Fits header object name for flats")
    parser.add_argument("--CRR", default=False, help="reject cosmic rays",
                        action="store_true")
    parser.add_argument("--dark_exptime", default=150.0,
                        help="Dark exposure time in second")

    args = parser.parse_args()

    ic = ImageFileCollection(args.path, glob_include=args.include,
                             glob_exclude=args.exclude)

    # import IPython
    # IPython.embed()
    if args.verbose:
        print(ic.summary)

    if True:
        print("Creating bias")
        predicate = {"EXPTYPE": "Bias", "BINNING": "1x1"}
        cc = collect_set(ic, predicate, ".")
        print("Combining bias")
        master_bias = combine_collection(cc, diagnostic=True)
        write_comb(master_bias, name="bias")
        pl.savefig("OUT/noise.pdf")
    else:
        master_bias = {}
        for i in range(1,5):
            HDU = astropy.io.fits.open("OUT/bias_%i.fits" % i)
            master_bias[i] = astropy.nddata.CCDData(HDU[0].data,
                                                    unit=u.electron)

    if True:
        print("Creating darks")
        predicate = {"EXPTYPE": "Dark", "BINNING": "1x1", "EXPTIME": 150.0}
        cc = collect_set(ic, predicate, ".", bias=master_bias, gain_corrected=True)
        print("Combining darks")
        master_darks = combine_collection(cc)
        write_comb(master_darks, name="dark")

    for filter_ in set(ic.values("filter")):
        predicate = {"EXPTYPE": "Flat", "FILTER": filter_, "BINNING": "1x1",
                     "OBJECT": args.flatname}

        if True:
            print("Creating flat for %s" % filter_)
            for name, bias in [("flat_debiased_%s" % filter_, master_bias)]:
                cc = collect_set(ic, predicate, ".", bias=master_bias,
                                 gain_corrected=True)
                print("Combining flats")
                master_flats = combine_collection(cc)
                write_comb(master_flats, name=name)
        else:
            master_flats = {}
            for i in range(1,5):
                HDU = astropy.io.fits.open("OUT/flat_debiased_r_%i.fits" % i)
                master_flats[i] = astropy.nddata.CCDData(HDU[0].data,
                                                    unit=u.electron)

        for object_ in set(ic.values("object")):
            print(object_)
            #if (type(object_) is not str) or (type(object_) is not np.str_):
            #    object_ = "undefined"

            predicate = {"EXPTYPE": "Object", "FILTER": filter_,
                         "BINNING": "1x1", "OBJECT": object_,
                         "NAXIS1": 2176, "NAXIS2": 2184}

            print("Handling %s/%s" % (object_, filter_))
            cc = collect_set(ic, predicate, ".",
                             bias=master_bias,
                             flat=master_flats,
                             gain_corrected=True,
                             dark_exposure_time=None, CRR=args.CRR)
            if len(cc[1]) == 0: continue

            print("Writing science: %s" % object_)
            write_collection(cc, outdir="OUT/%s_%s" % (format_filename(object_),
                                                       filter_))
