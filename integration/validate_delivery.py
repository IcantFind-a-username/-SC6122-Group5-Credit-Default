"""Render and mechanically check delivered documents against accepted metrics."""
import json
from pathlib import Path
import re

import fitz
from PIL import Image
from pptx import Presentation

from integration.artifacts import file_hash, write_json
from integration.audit import read_csv

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'submission'


def run():
    rendered = OUT/'rendered'
    rendered.mkdir(exist_ok=True)
    pdf = fitz.open(OUT/'Group5_Final_Report.pdf')
    print('Report page openings:', [(i+1, p.get_text()[:100]) for i,p in enumerate(pdf)])
    report_text = '\n'.join(p.get_text() for p in pdf)
    for text in ['Problem','References','contribution','hypothetical','post-hoc']:
        assert text.lower() in report_text.lower(), text
    test = read_csv(ROOT/'results/final/model_comparison.csv')
    test = test[(test.Partition=='test') & (test.Threshold==.5)]
    for _, row in test.iterrows():
        for key in ['AP','ROC-AUC','Precision','Recall','F1','Accuracy']:
            assert f'{row[key]:.4f}' in report_text, (row.Model,key)
    pages = []
    for i,page in enumerate(pdf):
        spans=[s for block in page.get_text('dict')['blocks'] if 'lines' in block for line in block['lines'] for s in line['spans']]
        outside=[s['text'] for s in spans if s['bbox'][0]<20 or s['bbox'][2]>page.rect.width-20 or s['bbox'][3]>page.rect.height-20]
        assert not outside, (i+1,outside)
        page.get_pixmap(matrix=fitz.Matrix(1,1)).save(rendered/f'report_page_{i+1}.png')
        pages.append({'page':i+1,'words':len(page.get_text().split()),'min_font_pt':round(min(s['size'] for s in spans),2),
                      'rightmost_text_pt':round(max(s['bbox'][2] for s in spans),2)})
    sheet=Image.new('RGB',(1290,((len(pdf)+2)//3)*610),'#dae0e6')
    for i in range(len(pdf)):
        im=Image.open(rendered/f'report_page_{i+1}.png').convert('RGB')
        im.thumbnail((420,594))
        sheet.paste(im,((i%3)*430,(i//3)*610))
    sheet.save(rendered/'report_contact.png')
    result={'report_pages':len(pdf),'report_page_details':pages,
            'report_comparison_numbers':'All baseline/tuned 0.5 numeric metrics found in PDF',
            'report_pdf_SHA256':file_hash(OUT/'Group5_Final_Report.pdf'), 'report_latex_SHA256':file_hash(OUT/'Group5_Final_Report.tex'),
            'visual_inspection':'Rendered contact sheet and full pages are separately inspected; automated bounds do not alone establish visual quality.'}
    if (OUT/'Group5_Presentation.pdf').exists():
        deck=Presentation(str(OUT/'Group5_Presentation.pptx'))
        slides_pdf=fitz.open(OUT/'Group5_Presentation.pdf')
        assert len(deck.slides)==len(slides_pdf)==16
        for slide,page in zip(deck.slides,slides_pdf):
            strings=[s.text for s in slide.shapes if s.has_text_frame and s.text.strip()]
            title=max(strings,key=lambda text: len(text)) if not strings else strings[0]
            def normalized(text):
                return re.sub(r'[^a-z0-9]','',text.lower())
            assert normalized(title) in normalized(page.get_text()), title
        result.update({'slide_pages':len(slides_pdf),'slide_first_text_matches_pdf':True,
                       'presentation_pptx_SHA256':file_hash(OUT/'Group5_Presentation.pptx'),
                       'presentation_pdf_SHA256':file_hash(OUT/'Group5_Presentation.pdf')})
    assert len(pdf) <= 7, f'Report has {len(pdf)} pages'
    write_json(OUT/'delivery_validation.json',result)
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    run()
