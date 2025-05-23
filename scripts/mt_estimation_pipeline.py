import argparse
import multiprocessing as mp
import time
from functools import partial
from pathlib import Path

import numpy as np

from hcpasl.MTEstimation import estimate_mt, setup_mtestimation

TR = 8
ROIS = {
    "wm": ["wm"],
    "gm": ["gm"],
    "csf": ["csf"],
    "combined": ["combined"],
    "all": ["wm", "gm", "csf", "combined"],
}


def main():
    # argument handling
    parser = argparse.ArgumentParser(
        description="Run the empirical banding estimation pipeline."
    )
    parser.add_argument(
        "--studydir", help="Path to the study's base directory.", required=True
    )
    parser.add_argument(
        "--subjectlist",
        help="A .txt file of subject names from whom we "
        + "wish to estimate the empirical banding scaling factors.",
        required=True,
    )
    parser.add_argument(
        "--roi",
        help="Tissue in which to estimate the empirical banding scaling factors.",
        default="combined",
        choices=("combined", "wm", "gm", "csf", "all"),
    )
    parser.add_argument(
        "--method",
        help="Whether to estimate the empirical banding scaling factors for the central "
        + "4 bands separately or together.",
        default="separate",
        choices=("separate", "together"),
    )
    parser.add_argument(
        "-g",
        "--grads",
        help="Filename of the gradient coefficients for gradient"
        + "distortion correction.",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--out",
        help="Directory in which to save empirical banding estimates. By default "
        + "they will be saved in the current working directory.",
        default=Path.cwd(),
    )
    parser.add_argument(
        "--ignore_dropouts",
        help="Whether to ignore Dropout voxels (as estimated by the "
        + "SE-based approach) when estimating the empirical banding scaling "
        + "factors.",
        action="store_true",
    )
    parser.add_argument(
        "-c",
        "--cores",
        help="Number of cores to use. Default is 1.",
        default=1,
        type=int,
        choices=range(1, mp.cpu_count() + 1),
    )
    parser.add_argument(
        "--interpolation",
        help="Interpolation order for registrations. This can be any "
        + "integer from 0-5 inclusive. Default is 3. See scipy's "
        + "map_coordinates for more details.",
        default=3,
        type=int,
        choices=range(0, 5 + 1),
    )
    parser.add_argument(
        "-v", "--verbose", help="Print some useful statements.", action="store_true"
    )
    parser.add_argument(
        "--time",
        help="Print mean running time per subject for the setup section.",
        action="store_true",
    )
    parser.add_argument(
        "--no_refresh",
        help="Don't recreate intermediate files if they already exist. "
        + "This option is switched off by default.",
        action="store_false",
    )

    # parse
    args = parser.parse_args()
    if args.time:
        start = time.time()
    studydir = Path(args.studydir).resolve(strict=True)
    subjects = Path(args.subjectlist).resolve(strict=True)
    subjects = np.loadtxt(subjects, dtype=str)
    subjects = [studydir / subid for subid in subjects.reshape(-1)]
    rois = ROIS[args.roi]
    if args.verbose:
        print(f"Your study directory is {studydir}.")
        print(f"You are processing {len(subjects)} subjects.")
        print(f"Rois to be used for the estimation: {rois}.")

    # do setup
    setup_call = partial(
        setup_mtestimation,
        rois=rois,
        coeffs_path=args.grads,
        interpolation=args.interpolation,
        ignore_dropouts=args.ignore_dropouts,
        force_refresh=args.no_refresh,
    )
    with mp.Pool(args.cores) as pool:
        results = pool.map(setup_call, subjects)
    successful_subs = []
    for result in results:
        print(result)
        if result[1] == 1:
            successful_subs.append(result[0])

    if args.time:
        end = time.time()
        print(f"Time per subject: {(end-start)*args.cores/(len(subjects)*60)} minutes.")
    # do estimation
    errors = estimate_mt(
        successful_subs,
        rois=rois,
        tr=TR,
        method=args.method,
        outdir=args.out,
        ignore_dropouts=args.ignore_dropouts,
    )
    for error in errors:
        print(error)


if __name__ == "__main__":
    main()
