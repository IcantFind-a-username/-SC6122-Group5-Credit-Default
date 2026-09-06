"""Refresh only artifact-reading notebooks; do not rerun source-writing notebooks."""
import json
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager

from integration.artifacts import write_json

ROOT = Path(__file__).resolve().parents[1]


def make_reader(title, folder, introduction):
    return nbformat.v4.new_notebook(cells=[
        nbformat.v4.new_markdown_cell(f'# {title}\n\n{introduction}\n\nThis notebook reads frozen artifacts only. See README for separate retraining commands.'),
        nbformat.v4.new_code_cell('from pathlib import Path\nimport json\nfrom IPython.display import display\nfrom integration.audit import read_csv\n\nROOT = Path.cwd()\nassert (ROOT / "data/splits/test.csv").exists(), "Run from repository root"\nOUT = ROOT / "results" / '+repr(folder)+'\nprotocol = json.loads((OUT / "protocol_frozen.json").read_text())\nprint(protocol.get("Evidence_status", "Historical frozen experiment; see integration audit for chronology"))\ndisplay(protocol["Selected_parameters"])'),
        nbformat.v4.new_code_cell('display(read_csv(OUT / "cv_results.csv").sort_values("Mean_CV_AP", ascending=False).head())\ndisplay(read_csv(OUT / "test_metrics.csv")[["Model","Threshold","AP","ROC-AUC","Precision","Recall","F1","Accuracy","TN","FP","FN","TP","Cost_5","Alert_rate"]])'),
        nbformat.v4.new_code_cell('display(read_csv(OUT / "bootstrap_intervals.csv"))\ndisplay(read_csv(OUT / "validation_importance.csv").head(10))'),
        nbformat.v4.new_markdown_cell('AP is average_precision_score, not trapezoidal PR-AUC. Bootstrap intervals condition on fixed predictions, model and thresholds; no retraining or threshold-selection uncertainty is included. Importance is associative, not causal.')
    ], metadata={'kernelspec': {'display_name':'SC6122 unified environment','language':'python','name':'sc6122'}})


def run():
    write_json(ROOT / 'results/final/notebook_status.json', {'Status':'Started','Note':'01/02 are retained historical source-writing notebooks; do not rerun over frozen data.'})
    nbformat.write(make_reader('Logistic regression — reproducibility supplement','logistic_supplement',
        '**Provenance:** the original 03 notebook was an empty file. Its historical CSVs remain unchanged. This notebook displays a separate post-hoc supplement, not recovered original training or an independent unseen-test experiment.'), ROOT/'03_logistic_regression.ipynb')
    nbformat.write(make_reader('Random forest — frozen evidence','rf',
        'Model regeneration under scikit-learn 1.8.0 is documented in Git history; no new test optimization occurs here.'), ROOT/'05_random_forest.ipynb')
    manager=KernelSpecManager(kernel_dirs=[str(ROOT/'.venv/share/jupyter/kernels')])
    records=[]
    for name in ['03_logistic_regression.ipynb','04_decision_tree.ipynb','05_random_forest.ipynb','06_xgboost.ipynb']:
        path=ROOT/name
        notebook=nbformat.read(path,as_version=4)
        notebook.metadata.kernelspec={'display_name':'SC6122 unified environment','language':'python','name':'sc6122'}
        for cell in notebook.cells:
            if cell.cell_type=='code':
                cell.outputs=[]
                cell.execution_count=None
        km=KernelManager(kernel_name='sc6122',kernel_spec_manager=manager)
        executed=NotebookClient(notebook,timeout=180,kernel_name='sc6122',km=km,
                                resources={'metadata':{'path':str(ROOT)}})
        executed.execute()
        nbformat.write(notebook,path)
        records.append({'notebook':name,'code_cells':sum(c.cell_type=='code' for c in notebook.cells),'status':'Executed successfully in unified environment'})
    write_json(ROOT/'results/final/notebook_status.json',{'Status':'Passed','Executed':records,
        'Not_executed':{'01_data_inspection.ipynb':'Historical network/source inspection; source audit independently verifies data.',
                        '02_preprocessing.ipynb':'Historical writer would overwrite frozen data; independent source and membership audit replaces rerun.'}})
    print(json.dumps(records,indent=2))


if __name__=='__main__':
    run()
