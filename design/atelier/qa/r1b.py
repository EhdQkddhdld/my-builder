"""ATELIER R1b: neutral navigation and actual selected-chip count checks."""
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
categories={'style':['style'],'person':['count','char','cloth','appearance','body','react'],'composition':['pose','cam'],'direction':['env','light','intensity','advanced']}
results=[]
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
                page.wait_for_function("typeof window.rdV30Route==='function' && document.querySelectorAll('.atelier-category').length===5")
                page.evaluate("window.rdV30Route('builder')")
                state=page.evaluate('JSON.stringify(captureState())')
                undo=page.locator('#btn-undo').is_disabled()
                panel=page.locator('#rd-atelier-category-panel')
                for key,expected in categories.items():
                    button=page.locator('[data-atelier-category="'+key+'"]')
                    button.click()
                    assert panel.is_visible(),key
                    assert button.get_attribute('aria-pressed')=='true',key
                    assert panel.locator('[data-detail]').evaluate_all('(nodes)=>nodes.map(n=>n.dataset.detail)')==expected,key
                    assert page.locator('.rd302-index-card[data-detail]').count()==13,'duplicate or missing original card'
                    assert page.evaluate('JSON.stringify(captureState())')==state,key
                    assert page.locator('#btn-undo').is_disabled()==undo,key
                    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),key
                page.locator('[data-atelier-category="style"]').click()
                expected=page.evaluate("getActiveValues('group-style').length")
                assert int(page.locator('[data-atelier-category="style"] .atelier-count').text_content())==expected
                # Neutral lighting: use existing selection controls and existing undo.
                page.locator('[data-atelier-category="direction"]').click()
                before=page.evaluate('JSON.stringify(captureState())')
                badge=page.locator('[data-atelier-category="direction"] .atelier-count')
                n=int(badge.text_content())
                old_light=page.evaluate("getActiveValues('group-light').length")
                panel.locator('[data-detail="light"]').click()
                page.locator('body.rd302-detail-open').wait_for()
                assert not panel.is_visible()
                chip=page.locator('#group-light .chip[data-val]:not(.active):not(.locked):not(.dimmed):visible').first
                assert chip.count()==1,'no selectable light'
                chip.click()
                new_light=page.evaluate("getActiveValues('group-light').length")
                page.wait_for_function("(n)=>Number(document.querySelector('[data-atelier-category=direction] .atelier-count').textContent)===n",arg=n+new_light-old_light)
                assert page.evaluate('JSON.stringify(captureState())')!=before
                assert page.evaluate('window.rdHandleBack()') is True
                page.locator('body:not(.rd302-detail-open)').wait_for()
                assert panel.is_visible()
                page.locator('#rd-v27-undo').click()
                page.wait_for_function("(s)=>JSON.stringify(captureState())===s",arg=before)
                page.wait_for_function("(n)=>Number(document.querySelector('[data-atelier-category=direction] .atelier-count').textContent)===n",arg=n)
                page.locator('[data-atelier-category="composition"]').click()
                assert page.locator('[data-atelier-category="clothes"],[data-atelier-category="background"]').count()==0
                assert page.locator('[data-atelier-category="studio"] .atelier-count').is_hidden()
                page.locator('[data-atelier-category="studio"]').click()
                page.wait_for_function("window.rdV30Current()==='studio'")
                assert not page.evaluate('window.rdNai.isBusy()'), 'studio navigation unexpectedly started generation'
                assert page.evaluate('JSON.stringify(captureState())')==before
                assert page.evaluate('window.rdHandleBack()') is True
                page.wait_for_function("window.rdV30Current()==='builder'")
                assert panel.is_visible()
                assert page.locator('[data-atelier-category="composition"]').get_attribute('aria-pressed')=='true'
                assert page.evaluate('JSON.stringify(captureState())')==before
                page.screenshot(path=str(OUT/f'category-{width}x{height}.png'))
                page.locator('#rd-v30-step4').click()
                assert not panel.is_visible()
                assert page.evaluate("document.body.dataset.rdStep==='step-4'")
                assert page.evaluate('JSON.stringify(captureState())')==before
                page.evaluate("window.rdV30Route('home')")
                assert not page.locator('#step-nav').is_visible()
                assert not errors,errors
                result['status']='PASS'
            except Exception as e:
                result['error']=repr(e)
                result['page_errors']=errors
            finally:
                context.close()
                results.append(result)
                (OUT/'categories.json').write_text(json.dumps(results,indent=2,ensure_ascii=False))
        browser.close()
finally:
    server.shutdown()
print(json.dumps(results,indent=2,ensure_ascii=False))
assert all(r['status']=='PASS' for r in results),'category regression failed'
