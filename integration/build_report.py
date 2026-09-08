"""Generate publication figures and LaTeX report from accepted predictions/metrics.

Artifact-only presentation of frozen evidence; no fitting or decision selection.
"""
import json
import re
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from integration.artifacts import file_hash, write_json
from integration.audit import read_csv
from integration.presentation_evidence import rf_interpretation

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'submission'
FIG = OUT / 'figures'
NAVY, TEAL, ORANGE, GREY = '#142C43', '#127D88', '#D76B38', '#65788A'
FAMILIES = [('logistic_supplement', 'Logistic Regression', 'LR*'),
            ('decision_tree', 'Decision Tree', 'DT'), ('rf', 'RF', 'RF'), ('xgboost', 'XGBoost', 'XGB')]


def table(headers, rows, spec=None):
    spec = spec or ('l' + 'r' * (len(headers) - 1))
    return ('\\begin{tabular}{@{}' + spec + '@{}}\\toprule\n' +
            ' & '.join(headers) + '\\\\\\midrule\n' +
            '\n'.join(' & '.join(map(str, row)) + '\\\\' for row in rows) +
            '\n\\bottomrule\\end{tabular}')


def save_figure(fig, name):
    fig.savefig(FIG / f'{name}.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)


def run():
    FIG.mkdir(parents=True, exist_ok=True)
    comparison = read_csv(ROOT / 'results/final/model_comparison.csv')
    test = comparison[comparison.Partition == 'test']
    original_lr = read_csv(ROOT/'results/logistic_regression_final_comparison.csv')
    original_lr = original_lr[original_lr.Model == 'Baseline LR'].iloc[0]
    audit = json.loads((ROOT / 'results/final/audit.json').read_text())
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'text.color': NAVY,
                         'axes.spines.top': False, 'axes.spines.right': False})
    performance, counts, configs, costs, ranking = [], [], [], [], []
    selected_rows = {}
    config_text = {'LR*': 'C=0.1; unweighted', 'DT': 'Unlimited depth; leaf=100',
                   'RF': '500 trees; depth=8; leaf=2; class 1:3',
                   'XGB': '150 trees; depth=4; rate=.03; weight=3'}
    for folder, family, label in FAMILIES:
        subset = test[(test.Family == family) & (test.Threshold == .5)]
        for prefix, abbr in [('Baseline', 'B'), ('Tuned', 'T')]:
            row = subset[subset.Model.str.startswith(prefix)].iloc[0]
            performance.append([f'{label} {abbr}'] + [f'{row[k]:.4f}' for k in ['AP','ROC-AUC','Precision','Recall','F1','Accuracy']])
            counts.append([f'{label} {abbr}'] + [str(int(row[k])) for k in ['TN','FP','FN','TP']])
            selected_rows[f'{label}_{abbr}'] = row
        ranking.append((label, selected_rows[f'{label}_B'].AP, selected_rows[f'{label}_T'].AP))
        protocol = json.loads((ROOT / f'results/{folder}/protocol_frozen.json').read_text())
        cv = read_csv(ROOT / f'results/{folder}/cv_results.csv')
        best = cv[cv.Candidate == protocol['Selected_candidate']].iloc[0]
        configs.append([label, str(protocol['Candidates']), str(protocol['Candidates']*5), config_text[label], f'{best.Mean_CV_AP:.4f}'])
        if family != 'Decision Tree':
            for policy, model in [('0.5', selected_rows[f'{label}_T'].Model), ('Val r=5', selected_rows[f'{label}_T'].Model + ' / cost ratio 5')]:
                row = test[(test.Family == family) & (test.Model == model)].iloc[0]
                costs.append([label, policy, f'{row.Threshold:.5f}', f'{row.Recall*100:.2f}',
                              f'{row.Alert_rate*100:.2f}', str(int(row.FP)), str(int(row.FN)), str(int(row.Cost_5))])
    fig, ax = plt.subplots(figsize=(5.5, 2.05), layout='constrained')
    positions = np.arange(4)
    for offset,index,label,color in [(-.18,1,'Baseline',GREY),(.18,2,'CV-selected',TEAL)]:
        ax.bar(positions+offset,[r[index] for r in ranking],.34,label=label,color=color)
    ax.axhline(1327/6000,ls='--',color=ORANGE,lw=1,label='Test prevalence')
    ax.set(xticks=positions,xticklabels=[r[0] for r in ranking],ylim=(0,.68),ylabel='Average precision (AP)')
    ax.legend(ncol=3,fontsize=8,loc='lower left',bbox_to_anchor=(0,1.02),
              borderaxespad=0,frameon=False)
    ax.grid(axis='y',alpha=.15)
    save_figure(fig,'ranking')
    base=selected_rows['XGB_T']
    selected=test[(test.Family=='XGBoost') & (test.Model=='Tuned XGBoost / cost ratio 5')].iloc[0]
    fig, axes=plt.subplots(1,3,figsize=(5.5,2.0), layout='constrained')
    for ax,key,title in zip(axes,['FP','FN','Cost_5'],['False positives','Missed defaults','Cost: FP + 5 FN']):
        bars=ax.bar(['0.5','Validation t'],[base[key],selected[key]],color=[GREY,ORANGE],width=.6)
        ax.bar_label(bars,fmt='%.0f',padding=4,fontsize=9)
        ax.set(title=title,ylim=(0,max(base[key],selected[key])*1.25))
        ax.title.set_fontsize(9)
        ax.tick_params(labelsize=8.5)
        ax.grid(axis='y',alpha=.12)
    save_figure(fig,'cost_tradeoff')
    rf_importance, rf_examples = rf_interpretation()
    imp=rf_importance.head(6).iloc[::-1]
    fig,ax=plt.subplots(figsize=(5.5,2.05), layout='constrained')
    ax.barh(imp.Feature,imp.Mean_AP_decrease,xerr=imp.SD_AP_decrease,color=TEAL,capsize=3)
    ax.set(xlabel='Decrease in validation AP after permutation')
    ax.grid(axis='x',alpha=.12)
    save_figure(fig,'importance')
    values = {'CONFIG_TABLE':table(['Model','Configs','CV fits','Selected (summary)','CV AP'], configs, 'lrrp{47mm}r'),
              'PERFORMANCE_TABLE':table(['Model','AP','ROC-AUC','P','R','F1','Acc'],performance),
              'CONFUSION_TABLE':table(['Model','B: TN','FP','FN','TP','T: TN','FP','FN','TP'], [[counts[i][0].split()[0]] + counts[i][1:] + counts[i+1][1:] for i in range(0,len(counts),2)]),
              'COST_TABLE':table(['Model','Policy','Threshold','Recall \\%','Alert \\%','FP','FN','Cost'],costs),
              'DUP_TEST':str(audit['details']['source']['test_rows_features_seen_in_development']),
              'FIT_POS':str(audit['details']['source']['fit_defaults']),
              'LR_BASE_AP':f"{selected_rows['LR*_B'].AP:.4f}", 'LR_TUNE_AP':f"{selected_rows['LR*_T'].AP:.4f}",
              'LR_ORIG_ACC':f'{original_lr.Accuracy:.4f}',
              'LR_ORIG_AUC':f"{original_lr['ROC-AUC']:.4f}",
              'LR_ORIG_REC':f'{original_lr.Recall:.4f}',
              'XGB_THR':f'{selected.Threshold:.5f}',
              'XGB_REDUCTION':f'{100*(base.Cost_5-selected.Cost_5)/base.Cost_5:.2f}'}
    team = json.loads((OUT/'team.json').read_text())
    values['MEMBER_AUTHORS'] = (r' \\ '.join(
        r' \quad '.join(r'\textbf{' + member['name'] + '} (' + member['student_id'] + ')'
                      for member in team[start:start+2]) for start in (0, 2)) +
        r' \\ Nanyang Technological University \\ SC6122 Emerging Topics in FinTech --- Group 5')
    report_roles = {
        'Part 1': 'Data inspection/preprocessing; LR baseline and data characteristics',
        'Part 2': 'Decision-tree tuning, learned rules and overfitting control',
        'Part 3': 'Random-forest tuning, feature importance and error cases',
        'Part 4': 'XGBoost tuning and threshold trade-offs between missed defaults and false alarms',
    }
    values['MEMBER_CONTRIBUTIONS'] = (
        '\\begin{tabularx}{\\linewidth}{@{}p{30mm}Xr@{}}\\toprule\n'
        'Member / student ID & Responsibility and presentation & Share\\\\\\midrule\n' +
        '\n'.join('\\shortstack[l]{' + member['name'] + r'\\' + '\n' + member['student_id'] + '} & ' +
                  member['role'] + ': ' + report_roles[member['role']] + '; slides ' +
                  member['slides'].replace('–', '--') + ' & ' + str(member['share_percent']) + '\\%\\\\'
                  for member in team) + '\n\\bottomrule\\end{tabularx}')
    values['RF_TOP_IMPORTANCE'] = f'{rf_importance.iloc[0].Mean_AP_decrease:.4f}'
    values['RF_SECOND_IMPORTANCE'] = f'{rf_importance.iloc[1].Mean_AP_decrease:.4f}'
    for group, example in rf_examples.iterrows():
        values[f'RF_{group}_ROW'] = str(int(example.row_id))
        values[f'RF_{group}_SCORE'] = f'{example.Tuned_probability:.4f}'
        values[f'RF_{group}_PAY'] = str(int(example.PAY_0))
    template=(OUT/'report_template.tex').read_text()
    for key,value in values.items():
        template=template.replace('{{'+key+'}}',value)
    if re.search(r'\{\{[A-Z_]+\}\}', template):
        raise ValueError('Unresolved report field')
    (OUT/'Group5_Final_Report.tex').write_text(template)
    comparison.to_csv(OUT/'model_comparison.csv',index=False)
    read_csv(ROOT/'results/final/cost_comparison.csv').to_csv(OUT/'cost_comparison.csv',index=False)
    write_json(OUT/'report_build_provenance.json', {'comparison_SHA256':file_hash(ROOT/'results/final/model_comparison.csv'),
               'original_member_lr_SHA256':file_hash(ROOT/'results/logistic_regression_final_comparison.csv'),
               'generator_SHA256':file_hash(Path(__file__)), 'template_SHA256':file_hash(OUT/'report_template.tex'),
               'teacher_style_SHA256':file_hash(OUT/'neurips_2021.sty'),
               'teacher_style_unchanged':file_hash(OUT/'neurips_2021.sty') == file_hash(ROOT/'course_materials/latex_template/neurips_2021.sty')})
    print('Built report source and figures from audited comparison.')


if __name__ == '__main__':
    run()
