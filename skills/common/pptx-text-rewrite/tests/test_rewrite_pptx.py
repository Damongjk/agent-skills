import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt

spec = importlib.util.spec_from_file_location('rewrite_pptx', Path(__file__).resolve().parents[1] / 'scripts/rewrite_pptx.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class RewriteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / 'source.pptx'
        self.output = self.root / 'output.pptx'
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        paragraph = slide.shapes.add_textbox(Inches(1), Inches(1), Inches(8), Inches(1)).text_frame.paragraphs[0]
        first = paragraph.add_run(); first.text = 'Alpha '; first.font.bold = True; first.font.size = Pt(28); first.font.color.rgb = RGBColor(200, 10, 10)
        second = paragraph.add_run(); second.text = 'Beta'; second.font.italic = True; second.font.size = Pt(22); second.font.color.rgb = RGBColor(10, 20, 200)
        group = slide.shapes.add_group_shape()
        group.shapes.add_textbox(Inches(1), Inches(3), Inches(3), Inches(1)).text_frame.text = 'Alpha'
        slide.shapes.add_table(1, 1, Inches(1), Inches(4), Inches(3), Inches(1)).table.cell(0, 0).text = 'Alpha'
        prs.save(self.source)

    def tearDown(self): self.temp.cleanup()

    def test_mixed_styles_groups_tables_and_other_parts_survive(self):
        report = module.rewrite(self.source, self.output, [['Alpha', 'Gamma']])
        self.assertEqual(report['paragraphs_changed'], 3)
        self.assertFalse(report['skipped'])
        with zipfile.ZipFile(self.source) as old, zipfile.ZipFile(self.output) as new:
            self.assertEqual(old.namelist(), new.namelist())
            for name in old.namelist():
                if name not in report['parts_changed']: self.assertEqual(old.read(name), new.read(name))
            for name in report['parts_changed']:
                a, b = etree.fromstring(old.read(name)), etree.fromstring(new.read(name))
                props_a = [etree.tostring(e) for e in a.xpath('//a:rPr', namespaces=module.NS)]
                props_b = [etree.tostring(e) for e in b.xpath('//a:rPr', namespaces=module.NS)]
                self.assertEqual(props_a, props_b)
        prs = Presentation(self.output)
        runs = prs.slides[0].shapes[0].text_frame.paragraphs[0].runs
        self.assertEqual([r.text for r in runs], ['Gamma ', 'Beta'])
        self.assertTrue(runs[0].font.bold); self.assertTrue(runs[1].font.italic)

    def test_cross_run_phrase_is_preserved(self):
        report = module.rewrite(self.source, self.output, [['Alpha Beta', 'Gamma']])
        self.assertEqual(len(report['skipped']), 1)
        self.assertEqual(report['paragraphs_changed'], 0)
        with zipfile.ZipFile(self.source) as old, zipfile.ZipFile(self.output) as new:
            self.assertEqual(old.read('ppt/slides/slide1.xml'), new.read('ppt/slides/slide1.xml'))

    def test_no_source_or_existing_output_overwrite(self):
        with self.assertRaises(ValueError): module.rewrite(self.source, self.source, [])
        self.output.write_bytes(b'existing')
        with self.assertRaises(ValueError): module.rewrite(self.source, self.output, [])
        self.assertEqual(self.output.read_bytes(), b'existing')

    def test_longer_rules_are_applied_first(self):
        self.assertEqual(module.transform_text('Alpha Beta', sorted([['Alpha', 'Short'], ['Alpha Beta', 'Long']], key=lambda r:len(r[0]), reverse=True)), 'Long')

    def test_t2s_is_only_requested_and_context_conflicts_are_reported(self):
        from opencc import OpenCC
        self.assertEqual(module.transform_text('繁體', []), '繁體')
        self.assertEqual(module.transform_text('繁體', [], OpenCC('t2s')), '繁体')


if __name__ == '__main__': unittest.main()
