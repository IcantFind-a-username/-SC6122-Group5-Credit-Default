"""Unified artifact-only workflows; retraining is deliberately a separate command."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['verify','figures','notebooks','report','slides','package'])
    args = parser.parse_args()
    modules = {'verify':['integration.source_audit','integration.audit'],
               'figures':['integration.build_report'], 'notebooks':['integration.notebooks'],
               'report':['integration.build_report'], 'slides':['integration.build_slides']}
    for module in modules.get(args.mode, []):
        subprocess.run([sys.executable,'-m',module],cwd=ROOT,check=True)
    if args.mode == 'report':
        subprocess.run(['tectonic','submission/Group5_Final_Report.tex','--keep-logs'],cwd=ROOT,check=True)
    if args.mode == 'package':
        subprocess.run(['git','archive','--format=zip','--prefix=Group5/',
                        '--output=submission/Group5_Reproduction.zip','HEAD'],cwd=ROOT,check=True)
        print('Packaged committed HEAD only. Uncommitted files are not included.')


if __name__ == '__main__':
    main()
