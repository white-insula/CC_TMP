"""Track delivered PPTs and prevent regeneration from erasing later edits.

Run `python _delivery.py` after publishing or locally updating a delivered PPT.
Only inventories presentation files; does not rebuild or copy any presentations.
"""
from pathlib import Path
from datetime import datetime
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent.parent
OUTPUT = PROJECT / 'out/online_course'
REGISTRY = PROJECT / 'draft/ppt_delivery_registry.json'
REPORT = PROJECT / 'draft/ppt_delivery_status.md'


class ProtectedDeckError(RuntimeError):
    pass


def output_files(no):
    flat = [p for p in OUTPUT.glob('*.pptx')
            if re.match(r'^' + re.escape(no) + r'[_-]', p.name)]
    packaged = [p for folder in OUTPUT.glob(no + '_*') if folder.is_dir()
                for p in folder.glob('*.pptx')
                if re.match(r'^' + re.escape(no) + r'[_-]', p.name)]
    return sorted(flat + packaged)


def records():
    if not REGISTRY.exists():
        return {}
    return json.loads(REGISTRY.read_text(encoding='utf-8'))['lessons']


def assert_regeneration_allowed(no):
    """Fail before any writes; protect live outputs even if the ledger is stale."""
    no = str(no).zfill(2)
    entry = records().get(no, {})
    if output_files(no) or entry.get('protect_from_regeneration'):
        raise ProtectedDeckError(
            f'{no}讲已输出或已标记保护，禁止整讲重建，以免覆盖手工版式/动画。'
            '请按台账基于现有课件局部更新，备份后同步out；不要直接执行_lib.py覆盖。')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def refresh():
    previous = records()
    lessons = {}
    for n in range(1, 61):
        no = f'{n:02d}'
        sources = sorted((HERE/no).glob('*.pptx'))
        source = next((p for p in sources if p.name.startswith(no+'-')), None)
        outputs = output_files(no)
        old = previous.get(no, {})
        delivered = bool(outputs)
        same = bool(source and outputs and all(digest(source) == digest(p) for p in outputs))
        notes = old.get('notes', '')
        if no == '01':
            notes = '用户已手工调整版式，必须保留；P4已局部替换为GIF。'
        elif no == '03' and not notes:
            notes = '用户确认P2采用当前静图，不再补工厂车间视频。'
        elif no == '04' and not notes:
            notes = '用户已撤回输出；P6三张学生作品截图仍待向学生索取，补齐并重新确认后再输出。'
        elif no == '06' and not notes:
            notes = 'P4/P8已局部接入；演示录屏已按用户确认登记。'
        lessons[no] = {
            'status': '已输出' if delivered else '已撤回（待补素材）' if old.get('delivery_hold') else '曾输出，当前文件缺失' if old.get('protect_from_regeneration') else '未输出',
            'source': str(source.relative_to(PROJECT)) if source else None,
            'outputs': [{'path': str(p.relative_to(PROJECT)), 'sha256': digest(p)} for p in outputs],
            'source_sha256': digest(source) if source else None,
            'source_matches_output': same if delivered else None,
            'protect_from_regeneration': delivered or old.get('protect_from_regeneration', False),
            'manual_edits': '已确认（用户调整版式）' if no == '01' else old.get('manual_edits', '未确认；按可能含手工修改保护'),
            'manual_review': old.get('manual_review', '待用户整讲校验确认'),
            'delivery_hold': old.get('delivery_hold', False),
            'withdrawal': old.get('withdrawal'),
            'packages': [str(p.parent.relative_to(PROJECT)) for p in outputs
                         if p.parent != OUTPUT],
            'notes': notes,
        }
    timestamp = datetime.now().isoformat(timespec='seconds')
    REGISTRY.write_text(json.dumps({'updated_at': timestamp, 'lessons': lessons}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    published = [no for no, item in lessons.items() if item['outputs']]
    rows = [
        '# 微课PPT输出与防覆盖台账', '',
        f'更新时间：{timestamp}（本机时间）。当前已输出：'+ '、'.join(published)+'。', '',
        '本台账只记录PPT输出及版本状态；已输出不等于素材、来源授权或视频成片全部完成。', '',
        '## 执行规则', '',
        '- 先补素材并登记，再生成PPT，再手工加工；用户确认整讲人工校验通过后，才输出到out/online_course/。',
        '- 素材审核通过不等于整讲PPT校验通过；此前已有out文件保留并保护，未获整讲确认的一律注明待校验。',
        '- 已输出的讲次一律保护，禁止_lib.py/_ppt.build整讲重建；第01讲已有用户手工版式。',
        '- 后续局部更新前备份；源文件与out不一致时先判断哪份含最新手工修改，不直接互相覆盖。',
        '- 每个定稿微课用独立文件夹交付，含PPT、脚本Word、素材及清单；打包入口为python draft/online_course/_package_delivery.py。',
        '- 逐讲文件夹是唯一正式交付入口，不再另存根目录同内容PPT；未成包的历史输出待确认后归档。',
        '- 每次输出、替换或手工修改完成后刷新逐讲包清单，再运行python draft/online_course/_delivery.py刷新台账；源课件与逐讲包均须保护。',
        '- 文件实际存在于out时即受保护；已登记保护的文件即使被移走，也不自动解除保护。', '',
        '| 讲次 | 输出状态 | 人工校验 | 源课件与out | 整讲重建 | 交付文件夹 | 备注 |', '|---|---|---|---|---|---|---|',
    ]
    for no, item in lessons.items():
        match = ('一致' if item['source_matches_output'] else '不一致，需判断最新版本') if item['outputs'] else '—'
        packages = '、'.join(Path(p).name for p in item['packages']) or '—'
        rows.append(f"| {no} | {item['status']} | {item['manual_review']} | {match} | {'禁止' if item['protect_from_regeneration'] else '尚未输出；生成前检查手工修改'} | {packages} | {item['notes']} |")
    REPORT.write_text('\n'.join(rows)+'\n', encoding='utf-8')
    print('已输出：'+'、'.join(published))
    for no in published:
        print(no, '源/out一致' if lessons[no]['source_matches_output'] else '源/out不一致，保持两份原样')


if __name__ == '__main__':
    refresh()
