"""Navigation-only checks. Fresh browser contexts; all external network blocked."""
import json
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright

ROOT=Path.cwd()
OUT=ROOT/'qa-evidence'
OUT.mkdir(exist_ok=True)
server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(ROOT/'docs')))
Thread(target=server.serve_forever,daemon=True).start()
origin=f'http://127.0.0.1:{server.server_port}'
results=[]
def rect(page,sel):
    r=page.locator(sel).bounding_box()
    assert r is not None, f'Not visible: {sel}'
    return r
def assert_geometry(page,width,height,side):
    rail=rect(page,'#step-nav')
    shell=rect(page,'#rd-shell')
    toggle=rect(page,'#rd-atelier-rail-side')
    assert abs(rail['width']-56)<=1, rail
    assert toggle['width']>=44 and toggle['height']>=44,toggle
    assert rail['y']>=0 and rail['y']+rail['height']<=height+1,rail
    if side=='left':
        assert abs(rail['x'])<=1 and shell['x']>=rail['x']+rail['width']-1,(rail,shell)
    else:
        assert abs(rail['x']+rail['width']-width)<=1 and shell['x']+shell['width']<=rail['x']+1,(rail,shell)
    assert page.locator('#rd-atelier-rail-side').get_attribute('data-side')==side
    for button in page.locator('#step-nav > button:visible').all():
        r=button.bounding_box()
        assert r and r['width']>=44 and r['height']>=44,r
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1')
    return {'rail':rail,'shell':shell,'toggle':toggle}
try:
    with sync_playwright() as p:
        browser=p.chromium.launch()
        for width,height in [(476,660),(839,660),(840,660),(933,612)]:
            context=browser.new_context(viewport={'width':width,'height':height},reduced_motion='reduce',service_workers='block')
            context.route('**/*',lambda r:r.continue_() if r.request.url.startswith(origin+'/') and r.request.method in ('GET','HEAD') else r.abort())
            page=context.new_page()
            errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            result={'viewport':[width,height],'status':'FAIL'}
            try:
                response=page.goto(origin+'/index.html',wait_until='load')
                assert response and response.ok
                page.wait_for_function("typeof window.rdV30Route==='function' && !!document.getElementById('rd-atelier-rail-side')")
                assert not page.locator('#rd-atelier-rail-side').is_visible(), 'home rail exposed'
                page.evaluate("window.rdV30Route('builder')")
                page.locator('#rd-atelier-rail-side').wait_for(state='visible')
                initial='right' if width<840 else 'left'
                state=page.evaluate('JSON.stringify(captureState())')
                result['initial']=assert_geometry(page,width,height,initial)
                # Capture only the neutral initial editor screen; no user data or generation.
                page.screenshot(path=str(OUT/f'rail-{width}x{height}.png'))
                page.locator('#rd-atelier-rail-side').click()
                other='left' if initial=='right' else 'right'
                result['flipped']=assert_geometry(page,width,height,other)
                assert page.evaluate('JSON.stringify(captureState())')==state,'placement changed editor state'
                altwidth=933 if width<840 else 476
                page.set_viewport_size({'width':altwidth,'height':height})
                page.wait_for_function("(side)=>document.getElementById('rd-atelier-rail-side').dataset.side===side",arg=other)
                assert_geometry(page,altwidth,height,other)
                page.locator('#rd-atelier-rail-side').click()
                page.set_viewport_size({'width':width,'height':height})
                page.wait_for_function("(side)=>document.getElementById('rd-atelier-rail-side').dataset.side===side",arg=other)
                assert_geometry(page,width,height,other)
                page.reload(wait_until='load')
                page.wait_for_function("typeof window.rdV30Route==='function' && !!document.getElementById('rd-atelier-rail-side')")
                page.evaluate("window.rdV30Route('builder')")
                assert_geometry(page,width,height,other)
                page.evaluate("window.rdV30Route('home')")
                assert not page.locator('#rd-atelier-rail-side').is_visible(),'home rail exposed on return'
                assert not errors,errors
                result['status']='PASS'
            except Exception as e:
                result['error']=repr(e)
                result['page_errors']=errors
            finally:
                context.close()
                results.append(result)
                (OUT/'navigation.json').write_text(json.dumps(results,indent=2,ensure_ascii=False))
        browser.close()
finally:
    server.shutdown()
print(json.dumps(results,indent=2,ensure_ascii=False))
assert all(r['status']=='PASS' for r in results),'navigation regression failed'
