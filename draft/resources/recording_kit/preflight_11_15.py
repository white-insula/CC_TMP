"""Run existing static-image demos without GUI, in isolated temporary folders."""
from pathlib import Path
import contextlib, io, json, os, runpy, shutil, tempfile
from datetime import datetime
import cv2
import numpy as np

HERE=Path(__file__).resolve().parent
OUT=HERE/'_out/preflight_11_15';OUT.mkdir(parents=True,exist_ok=True)
jobs={'11':['numpy_image.py','colors.py'],'12':['read_check.py','read_fail.py','save.py'],'13':['identity.py'],'14':['red_block.py','blue_block.py','center.py'],'15':['split.py','merge.py','gray.py']}
results=[]
real_show,real_wait,real_move=cv2.imshow,cv2.waitKey,cv2.moveWindow
cwd=Path.cwd()
try:
    for no,scripts in jobs.items():
        for script in scripts:
            captures={}; moves=[];output=io.StringIO()
            cv2.imshow=lambda name,im:captures.__setitem__(name,im.copy())
            cv2.waitKey=lambda *_:0
            cv2.moveWindow=lambda *args:moves.append(args)
            with tempfile.TemporaryDirectory(prefix='mv_preflight_') as work:
                work=Path(work)
                for p in (HERE/no).iterdir():
                    if p.is_file():shutil.copy2(p,work/p.name)
                os.chdir(work)
                with contextlib.redirect_stdout(output):
                    try:runpy.run_path(str(work/script),run_name='__main__')
                    except SystemExit as exc:assert exc.code in (None,0)
                if script=='numpy_image.py':
                    assert captures['black'].shape==(300,400,3) and captures['black'].dtype==np.uint8
                    assert np.all(captures['black']==0)
                elif script=='colors.py':
                    for name,value in [('white',(255,255,255)),('red',(0,0,255)),('blue',(255,0,0))]:assert np.all(captures[name]==value)
                    assert len(moves)==3
                elif script=='read_check.py':assert captures['color'].ndim==3 and captures['gray'].ndim==2
                elif script=='read_fail.py':assert 'None' in output.getvalue() and not captures
                elif script=='save.py':
                    for ext in ['jpg','png']:assert cv2.imread('cat_copy.'+ext).shape==cv2.imread('cat.jpg').shape
                elif script=='identity.py':
                    im=cv2.imread('cat.jpg');hh,ww=im.shape[:2]
                    assert '中心' in output.getvalue() and im[hh//2,ww//2].size==3
                elif script in ('red_block.py','blue_block.py'):
                    value=(0,0,255) if script=='red_block.py' else (255,0,0)
                    assert np.all(captures['red block'][100:150,50:100]==value)
                elif script=='center.py':
                    hh,ww=captures['center'].shape[:2];assert np.all(captures['center'][hh//2-25:hh//2+25,ww//2-25:ww//2+25]==(0,255,0))
                elif script=='split.py':
                    im=cv2.imread('fruit.jpg')
                    for i,name in enumerate(['B','G','R']):assert np.array_equal(captures[name],im[:,:,i])
                elif script=='merge.py':
                    assert np.all(captures['no_blue'][:,:,0]==0)
                    assert np.array_equal(captures['swap'],captures['original'][:,:,::-1])
                elif script=='gray.py':assert np.array_equal(captures['gray'],cv2.cvtColor(cv2.imread('fruit.jpg'),cv2.COLOR_BGR2GRAY))
                for name,im in captures.items():cv2.imwrite(str(OUT/(no+'_'+Path(script).stem+'_'+name.replace(' ','_')+'.png')),im)
                results.append({'lesson':no,'program':script,'status':'passed','stdout':output.getvalue(),'images':{k:list(v.shape) for k,v in captures.items()},'window_positions':moves})
                os.chdir(cwd)
finally:
    os.chdir(cwd);cv2.imshow,cv2.waitKey,cv2.moveWindow=real_show,real_wait,real_move
result={'checked_at':datetime.now().isoformat(timespec='seconds'),'opencv':cv2.__version__,'numpy':np.__version__,'formal_recording':False,'gui_display_verified':False,'results':results}
(OUT/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'{len(results)} programs passed; no formal recordings created; source input files unchanged.')
