"""Scoped PPTX text replacement; unsafe cross-run paragraphs remain unchanged."""
import argparse
import json
from pathlib import Path
import re
import zipfile

from lxml import etree

NS = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}


def transform_text(text, rules, converter=None):
    for source, target in rules:
        text = text.replace(source, target)
    return converter.convert(text) if converter else text


def rewrite(source, output, rules, *, converter=None, include_notes=False, include_shared=False):
    source, output = Path(source), Path(output)
    if source.resolve() == output.resolve() or output.exists():
        raise ValueError('Use a new output path; source and existing outputs are never overwritten')
    if not isinstance(rules, list) or any(not isinstance(r, (list, tuple)) or len(r) != 2 or not all(isinstance(s, str) for s in r) or not r[0] for r in rules):
        raise ValueError('Rules must be pairs of nonempty source strings and target strings')
    rules = sorted(rules, key=lambda r: len(r[0]), reverse=True)
    report = {'paragraphs_changed': 0, 'parts_changed': [], 'skipped': [], 'scope': 'slide text paragraphs (including groups/tables); charts, SmartArt, images and embedded objects excluded'}
    changed = {}
    parser = etree.XMLParser(resolve_entities=False, no_network=True, remove_blank_text=False)
    with zipfile.ZipFile(source) as archive:
        infos = archive.infolist()
        if len({i.filename for i in infos}) != len(infos):
            raise ValueError('Duplicate ZIP entries require package repair first')
        if any(i.filename.startswith('_xmlsignatures/') for i in infos):
            raise ValueError('Digitally signed presentations require a separate signature-aware workflow')
        bad = archive.testzip()
        if bad: raise ValueError('Input ZIP integrity failure')
        for info in infos:
            path = info.filename
            selected = bool(re.fullmatch(r'ppt/slides/slide\d+\.xml', path))
            selected |= include_notes and bool(re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml', path))
            selected |= include_shared and bool(re.fullmatch(r'ppt/(?:slideMasters/slideMaster|slideLayouts/slideLayout)\d+\.xml', path))
            if not selected: continue
            raw = archive.read(info)
            root = etree.fromstring(raw, parser)
            count = 0
            for index, paragraph in enumerate(root.xpath('//a:p', namespaces=NS)):
                nodes = paragraph.xpath('.//a:t', namespaces=NS)
                old = [n.text or '' for n in nodes]
                full = ''.join(old)
                wanted = transform_text(full, rules, converter)
                if wanted == full: continue
                pieces = [transform_text(t, rules, converter) for t in old]
                unsafe = ''.join(pieces) != wanted or bool(paragraph.xpath('./a:br|./a:fld', namespaces=NS))
                if unsafe:
                    report['skipped'].append({'part': path, 'paragraph_index': index, 'reason': 'cross-run replacement, explicit break, or dynamic field; original retained', 'text': full})
                    continue
                for node, new in zip(nodes, pieces): node.text = new
                count += 1
            if count:
                changed[path] = etree.tostring(root, encoding='UTF-8', xml_declaration=True, standalone=True)
                report['parts_changed'].append(path)
                report['paragraphs_changed'] += count
        # Unselected and unchanged parts retain their uncompressed original bytes and metadata.
        with zipfile.ZipFile(output, 'x') as target:
            target.comment = archive.comment
            for info in infos:
                target.writestr(info, changed.get(info.filename, archive.read(info)))
    with zipfile.ZipFile(output) as target:
        if target.testzip(): raise ValueError('Output ZIP integrity failure')
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source', type=Path)
    p.add_argument('output', type=Path)
    p.add_argument('--rules', type=Path, required=True)
    p.add_argument('--report', type=Path, required=True)
    p.add_argument('--t2s', action='store_true')
    p.add_argument('--include-notes', action='store_true')
    p.add_argument('--include-shared', action='store_true')
    args = p.parse_args()
    if args.report.resolve() in {args.source.resolve(), args.output.resolve()} or args.report.exists():
        p.error('Report must be a separate new file')
    converter = None
    if args.t2s:
        from opencc import OpenCC
        converter = OpenCC('t2s')
    report = rewrite(args.source, args.output, json.loads(args.rules.read_text(encoding='utf-8-sig')), converter=converter, include_notes=args.include_notes, include_shared=args.include_shared)
    with args.report.open('x', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(json.dumps({'paragraphs_changed': report['paragraphs_changed'], 'skipped': len(report['skipped']), 'output': str(args.output)}, ensure_ascii=False))


if __name__ == '__main__': main()
