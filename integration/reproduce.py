"""Unified artifact-only workflows; retraining is deliberately a separate command."""
import argparse
from pathlib import Path
import subprocess
import sys
from zipfile import ZipFile

from integration.artifacts import file_hash, write_json

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['verify','figures','notebooks','report','slides','package'])
    parser.add_argument("--soffice", help="LibreOffice soffice executable, for actual PPTX PDF export")
    args = parser.parse_args()
    modules = {'verify':['integration.source_audit','integration.audit'],
               'figures':['integration.build_report'], 'notebooks':['integration.notebooks'],
               'report':['integration.build_report'], 'slides':['integration.build_slides']}
    for module in modules.get(args.mode, []):
        command = [sys.executable,'-m',module]
        if module == 'integration.build_slides' and args.soffice:
            command += ['--soffice', args.soffice]
        subprocess.run(command,cwd=ROOT,check=True)
    if args.mode == 'report':
        subprocess.run(['tectonic','submission/Group5_Final_Report.tex','--keep-logs'],cwd=ROOT,check=True)
    if args.mode == 'package':
        subprocess.run(['git','archive','--format=zip','--prefix=Group5/',
                        '--output=submission/Group5_Reproduction.zip','HEAD'],cwd=ROOT,check=True)
        archive = ROOT/'submission/Group5_Reproduction.zip'
        with ZipFile(archive) as handle:
            names = handle.namelist()
            required = ['submission/Group5_Final_Report.pdf','submission/Group5_Presentation.pptx',
                        'submission/Group5_Presentation.pdf','submission/Group5_Speaker_Notes.md',
                        'submission/Group5_QA.md','submission/SUBMISSION_CHECKLIST.md',
                        'data/source/uci_350_raw.csv','results/final/model_comparison.csv','README.md']
            assert all('Group5/'+name in names for name in required)
            forbidden = {'.git','.venv','__pycache__','.mypy_cache','.pytest_cache','.ruff_cache'}
            assert not any(forbidden.intersection(Path(name).parts) for name in names)
            assert not any(name.endswith('Group5_Reproduction.zip') for name in names)
            assert handle.testzip() is None
        commit = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        write_json(ROOT/'submission/package_manifest.json', {'packaged_commit':commit,
                   'archive_SHA256':file_hash(archive),'archive_bytes':archive.stat().st_size,
                   'entries':len(names),'required_deliverables_present':True,'forbidden_content_absent':True,
                   'scope':'Committed HEAD; archive/manifest self-excluded by export-ignore'})
        print('Packaged and checked committed HEAD only:',commit)


if __name__ == '__main__':
    main()
