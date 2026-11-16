"""Copy approved lessons into independent delivery folders, without regeneration.

Includes exact published PPT bytes, the existing single-lesson Word script,
referenced PPT media and approved original editing assets. No video probing.
Existing delivery folders are protected from wholesale replacement.
"""
from pathlib import Path
from datetime import datetime
from collections import deque
import csv, hashlib, json, posixpath, re, shutil, sys, zipfile
from xml.etree import ElementTree as ET

import _delivery, _lib

ROOT = _delivery.PROJECT
COURSE = _delivery.HERE
MANUAL = COURSE/'manual'
OUTPUT = _delivery.OUTPUT
STAGING = ROOT/'draft/delivery_staging'
REL_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def copy_checked(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    assert sha(source.read_bytes()) == sha(target.read_bytes()), target


def ppt_media(path):
    """Only referenced slide/layout/master media, excluding orphaned images."""
    found = {}
    external = []
    with zipfile.ZipFile(path) as z:
        slides = sorted(n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml', n))
        for slide in slides:
            page = int(re.search(r'slide(\d+)\.xml$', slide).group(1))
            queue = deque([slide]); seen = set()
            while queue:
                part = queue.popleft()
                if part in seen: continue
                seen.add(part)
                xml = ET.fromstring(z.read(part))
                used = {v for node in xml.iter() for k,v in node.attrib.items()
                        if k.startswith('{'+REL_NS+'}')}
                parent, name = posixpath.split(part)
                relpath = posixpath.join(parent, '_rels', name+'.rels')
                if relpath not in z.namelist(): continue
                for rel in ET.fromstring(z.read(relpath)):
                    kind = rel.get('Type','').rsplit('/',1)[-1]
                    target = rel.get('Target','')
                    if kind in ('slideLayout','slideMaster'):
                        queue.append(posixpath.normpath(posixpath.join(parent,target)))
                    elif kind in ('image','audio','video','media') and rel.get('Id') in used:
                        if rel.get('TargetMode') == 'External':
                            external.append({'page':page, 'target':target})
                            continue
                        media = posixpath.normpath(posixpath.join(parent,target))
                        item = found.setdefault(media, {'data':z.read(media), 'pages':set()})
                        item['pages'].add(page)
    return found, external


def build_package(no, entry, registration, recordings, decisions, replacements, batch):
    c = _lib.load(no)
    folder_name = no+'_'+c.NAME
    destination = OUTPUT/folder_name
    if destination.exists():
        raise RuntimeError(f'{destination} 已存在，请按局部更新流程维护，不整包覆盖。')
    final_files = _delivery.output_files(no)
    flat = [p for p in final_files if p.parent == OUTPUT]
    if len(flat) > 1: raise RuntimeError(f'{no}: 正式PPT不唯一，请先核对输出台账。')
    # New deliveries copy the user-approved source straight into its lesson
    # folder; do not require or recreate a duplicate PPT at the output root.
    ppt = flat[0] if flat else COURSE/no/(no+'-'+c.NAME+'.pptx')
    if not ppt.is_file(): raise FileNotFoundError(ppt)
    word = COURSE/no/('脚本'+no+'.docx')
    if not word.is_file(): raise FileNotFoundError(word)
    package = batch/folder_name
    package.mkdir(parents=True)
    ppt_name = no+'-'+c.NAME+'.pptx'
    copy_checked(ppt, package/ppt_name)
    copy_checked(word, package/word.name)
    assets = {}

    def add_asset(data, filename, source, row=None, pages=(), category=None):
        key = sha(data)
        if key not in assets:
            suffix = Path(filename).suffix.lower()
            category = category or ('动画与视频' if suffix in ('.gif','.mp4','.mov','.avi','.mkv','.webm') else '音频' if suffix in ('.mp3','.wav','.m4a') else '图片')
            relative = Path('素材')/category/filename
            target = package/relative
            if target.exists() and sha(target.read_bytes()) != key:
                relative = relative.with_name(relative.stem+'_'+key[:8]+relative.suffix)
                target = package/relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            assert sha(target.read_bytes()) == key
            assets[key] = {'file':relative.as_posix(), 'sha256':key, 'sources':[],
                           'ppt_pages':[], 'registration':[]}
        item = assets[key]
        if source not in item['sources']: item['sources'].append(source)
        item['ppt_pages'] = sorted(set(item['ppt_pages']) | set(pages))
        if row and row not in item['registration']: item['registration'].append(row)

    for row in registration:
        if str(int(row['节'])) != str(int(no)) or row['状态'].strip() != '通过': continue
        if row['类型'] == 'ref': continue
        source = MANUAL/no/row['文件']
        if not source.is_file(): raise FileNotFoundError(f'已通过素材缺少原件：{source}')
        add_asset(source.read_bytes(), source.name, str(source.relative_to(ROOT)), row)
    for recording in recordings.get(no, {}).get('文件', []):
        source = Path(recording['原始文件'])
        if not source.is_file():
            source = source.with_name(recording['规范文件名'])
        if not source.is_file():
            raise FileNotFoundError(f'已登记录屏原文件不存在：{source}')
        add_asset(source.read_bytes(), recording['规范文件名'], str(source),
                  row={'页':str(recording['页']), '类型':'rec', '状态':'已录制（用户确认）'},
                  category='演示录屏')
    media, external = ppt_media(ppt)
    for name, item in sorted(media.items()):
        filename = f"{no}-p{min(item['pages']):02d}-内嵌-{Path(name).name}"
        add_asset(item['data'], filename, 'PPT:'+name, pages=item['pages'])

    files = [{'file':p.relative_to(package).as_posix(), 'sha256':sha(p.read_bytes()), 'bytes':p.stat().st_size}
             for p in sorted(package.rglob('*')) if p.is_file()]
    note = entry.get('notes','')
    manifest = {'lesson':no, 'name':c.NAME, 'review':entry['manual_review'],
                'published_ppt':str((destination/ppt_name).relative_to(ROOT)),
                'ppt_source':str(ppt.relative_to(ROOT)),
                'word_source':str(word.relative_to(ROOT)), 'files':files,
                'assets':list(assets.values()), 'external_media_links':external,
                'recording_status':recordings.get(no),
                'display_decisions':decisions.get(no,{}),
                'ppt_gif_replacements':replacements.get(no,{}), 'notes':note,
                'created_at':datetime.now().isoformat(timespec='seconds')}
    (package/'交付清单.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    overview = [f'# {no} {c.NAME} · 交付内容', '',
                f'- PPT：`{ppt_name}`', f'- 脚本 Word：`{word.name}`',
                f'- 素材：{len(assets)} 份，按图片、动画与视频分类；相同内容只保留一份。',
                '- PPT与Word均为原文件复制；本次未重新生成课件或修改脚本。',
                '- PPT内嵌素材按实际引用提取；另附已审核通过、供剪辑使用的原始素材。', '']
    if note: overview += ['## 当前制作状态', '', note, '']
    if recordings.get(no):
        recorded_files = recordings[no].get('文件', [])
        message = (f'已录制（用户确认）。本包附{len(recorded_files)}段规范命名的演示录屏，供视频公司剪辑；未检查播放。'
                   if recorded_files else '已录制（用户确认）。当前登记未提供原视频文件位置，本包保留完成记录；录屏由用户另行交视频公司。不据此重新列为未录制。')
        overview += ['## 演示录屏', '', message, '']
    if decisions.get(no):
        overview += ['## 已确认的展示方式', '']
        overview += [f'- P{p}：{text}' for p,text in decisions[no].items()]
        overview += ['']
    overview += ['## 素材清单', '', '| 文件 | PPT实际引用页 | 素材登记页 |', '|---|---|---|']
    for item in assets.values():
        pages = '、'.join('P'+str(p) for p in item['ppt_pages']) or '独立剪辑素材'
        registered = '、'.join(sorted({'P'+r['页'] for r in item['registration']})) or '从PPT提取'
        overview.append(f"| {item['file']} | {pages} | {registered} |")
    if external:
        overview += ['', '## PPT外链媒体', '']
        overview += [f"- P{item['page']}：{item['target']}（保留原引用，未下载外部链接）" for item in external]
    (package/'素材清单.md').write_text('\n'.join(overview)+'\n',encoding='utf-8')
    for item in files:
        assert sha((package/item['file']).read_bytes()) == item['sha256']
    return package, destination, manifest


def main():
    entries = _delivery.records()
    requested = [str(int(no)).zfill(2) for no in sys.argv[1:]]
    lessons = requested or [no for no,e in entries.items() if not e.get('packages') and not e.get('delivery_hold')
                            and ('用户确认可输出' in e.get('manual_review','') or e.get('manual_review','').startswith('已通过'))]
    if not lessons:
        print('暂无已获准但尚未建包的课件；已有逐讲包不重复生成。')
        return
    for no in lessons:
        if entries[no].get('delivery_hold'):
            raise RuntimeError(f'{no} 已撤回待补素材，用户重新批准前不得输出。')
        review = entries[no].get('manual_review','')
        if '用户确认可输出' not in review and not review.startswith('已通过'):
            raise RuntimeError(f'{no} 尚未获准输出，不能混作定稿交付。')
    with (MANUAL/'素材登记.csv').open(encoding='utf-8-sig',newline='') as f:
        registration = list(csv.DictReader(f))
    def load(name):return json.loads((MANUAL/name).read_text(encoding='utf-8'))
    batch = STAGING/datetime.now().strftime('%Y%m%d_%H%M%S')
    plans = [build_package(no,entries[no],registration,load('录屏完成登记.json'),
                           load('展示方式确认.json'),load('PPT动图替换.json'),batch) for no in lessons]
    # All packages are prepared and checked before publishing new directories.
    for prepared,destination,manifest in plans:
        assert prepared.resolve().is_relative_to(STAGING.resolve())
        assert destination.resolve().is_relative_to(OUTPUT.resolve())
        assert not destination.exists()
        prepared.rename(destination)
        # Remove only a verified, identical legacy flat copy after the complete
        # lesson folder has been successfully published.
        packaged_ppt = ROOT/manifest['published_ppt']
        for legacy in list(OUTPUT.glob(manifest['lesson']+'_*.pptx')):
            assert legacy.resolve().parent == OUTPUT.resolve()
            assert legacy.read_bytes() == packaged_ppt.read_bytes()
            legacy.unlink()
        print(manifest['lesson'],len(manifest['assets']),'assets ->',destination)
    report = ROOT/'draft/ppt_delivery_packages.json'
    previous = json.loads(report.read_text(encoding='utf-8')) if report.exists() else {}
    for _,destination,manifest in plans:
        previous[manifest['lesson']] = {'folder':str(destination.relative_to(ROOT)),
                                       'asset_count':len(manifest['assets']),
                                       'manifest':str((destination/'交付清单.json').relative_to(ROOT))}
    report.write_text(json.dumps(previous,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    _delivery.refresh()


if __name__ == '__main__': main()
