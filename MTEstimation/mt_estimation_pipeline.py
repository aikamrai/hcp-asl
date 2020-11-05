import argparse
from pathlib import Path
from setup_mt_estimation import setup_mtestimation
from estimate_MT import estimate_mt
import multiprocessing as mp
from functools import partial

TR = 8
hcp_dir = Path().home() / 'Documents/Data/HCP_data/Aging'
subjects = [
    'HCA7025253',
    'HCA6062456',
    'HCA6731574',
    'HCA6947294',
    'HCA6785193',
    'HCA6706373',
    'HCA6782995',
    'HCA6358881',
    'HCA6068670',
    'HCA6058970',
    'HCA6635679',
    'HCA7155973',
    'HCA6498190',
    'HCA6820674',
    'HCA6603969',
    'HCA7101546',
    'HCA6946191',
    'HCA7124659',
    'HCA6949399',
    'HCA6047359',
    'HCA6757390',
    'HCA7103651',
    'HCA6475986',
    'HCA6595794',
    'HCA6197580',
    'HCA6176471',
    'HCA6788199',
    'HCA7216462',
    'HCA6618679',
    'HCA6968202',
    'HCA6678495',
    'HCA7078981',
    'HCA6393176',
    'HCA7095779',
    'HCA6504866',
    'HCA6347674',
    'HCA6470673',
    'HCA7000843',
    'HCA6430257',
    'HCA6234964',
    'HCA7222154',
    'HCA6686191',
    'HCA6542470',
    'HCA7178177',
    'HCA7030751',
    'HCA6924080',
    'HCA7121350'
]
subject_dirs = []
for subject in subjects:
    subject_dirs.append(hcp_dir / subject)

rois = ['wm', 'gm', 'csf', 'combined']

setup_call = partial(setup_mtestimation, rois=rois)
with multiprocessing.Pool(multiprocessing.cpu_count()-2) as pool:
    results = pool.map(setup_call, subject_dirs)
for result in results:
    print(result)
estimate_mt(subject_dirs, rois, TR, 'together')

def main():
    # argument handling
    parser = argparse.ArgumentParser(
        description="Run the MT estimation pipeline."
    )
    parser.add_argument(
        "--subjectlist",
        help="A .txt file of subject names from whom we "
            +"wish to estimate the MT scaling factors.",
        required=True
    )
    parser.add_argument(
        "--studydir",
        help="Path to the study's base directory.",
        required=True
    )
    parser.add_argument(
        "--method",
        help="Method of bias correction to use. Default is "
            +"'calib'.",
        default='calib',
        choices=('calib', 't1', 'sebased')
    )
    parser.add_argument(
        "-c",
        "--cores",
        help="Number of cores to use. Default is the number "
            +f"of cores your machine has ({mp.cpu_count()}).",
        default=mp.cpu_count(),
        type=int,
        choices=range(1, mp.cpu_count()+1)
    )
    parser.add_argument(
        "--roi",
        help="Tissue in which to estimate the MT scaling factors.",
        default="combined",
        choices=("combined", "wm", "gm", "csf")
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Print some useful statements.",
        action="store_true"
    )

    # parse
    studydir = Path(args.studydir).resolve(strict=True)
    subjects = Path(args.subjects).resolve(strict=True)
    subjects = np.loadtxt(subjects)
    subjects = [studydir / subid for subid in subjects]
    if args.verbose:
        print(f"Your study directory is {studydir}.")
        print(f"You are processing {len(subjects)} subjects.")
    
