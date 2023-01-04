from curve_interpolation import curve_interpolation

def run(ep_csv, epp_csv, out_csv, logX, logY, skiprows):
    curve_int = curve_interpolation() # create the curve_interpolation object
    curve_int.master_curve(
        ep_csv=ep_csv,
        epp_csv=epp_csv,
        mc_file=out_csv,
        logX=logX,
        logY=logY,
        skiprows=0
        )
    return    

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--real_part_csv_dir", type=str,
        help='path to the csv file containing the real part data')
    parser.add_argument("-i", "--imag_part_csv_dir", type=str,
        help='path to the csv file containing the imaginary part data')
    parser.add_argument("-o", "--output_txt_dir", type=str, default='master_curve.txt',
        help='path to dump the output space delimited txt file containing the aligned master curve data')
    parser.add_argument("-x",'--logX', default=False, action='store_true',
        help='use log(x) for interpolation and extrapolation')
    parser.add_argument("-y",'--logY', default=False, action='store_true',
        help='use log(y) for interpolation and extrapolation')
    parser.add_argument("-s", "--skiprows", default=0, type=int,
        help='skiprows when loading csv, default to 0')
    args = parser.parse_args()

    run(
        ep_csv=args.real_part_csv_dir,
        epp_csv=args.imag_part_csv_dir,
        out_csv=args.output_csv_dir,
        logX=args.logX,
        logY=args.logY,
        skiprows=args.skiprows
        )