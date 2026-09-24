"""Data-backed scenes. Times are seconds on the FINAL component timeline."""
import html
import json


def esc(value):
    return html.escape(str(value))


def js(value):
    return json.dumps(value, ensure_ascii=False).replace('</', '<\\/')


def demo_frame(s, body):
    return (f'<div class="ev-paper"><div class="ev-heading">{esc(s["title"])}</div>'
            '<div class="ev-illustrative">Exemplo ilustrativo</div>'
            f'<div class="ev-work">{body}</div></div><div class="ev-footer">'
            f'<h2 class="ev-title">{esc(s.get("footer", ""))}</h2>'
            f'<p class="ev-copy">{esc(s.get("copy", ""))}</p></div>')


def scene(s, selector, asset_url):
    """Return trusted generated markup and deterministic, seekable GSAP instructions."""
    kind=s['type'];actions=[];a=s['start'];duration=s['end']-a
    if kind in ('image','evidence'):
        if s.get('mode','full' if kind=='image' else 'overlay')=='full':
            content=f'<img class="ev-art" src="{esc(asset_url)}"><div class="ev-art-label">{esc(s.get("title",""))}</div><div class="ev-credit">{esc(s.get("credit",""))}</div>'
        else:content=f'<img class="ev-reference" src="{esc(asset_url)}">'
    elif kind=='title':
        content=f'<h2 class="ev-title">{esc(s["title"])}</h2><p class="ev-copy">{esc(s.get("copy",""))}</p>'
    elif kind=='word':
        content=f'<div class="ev-word">{esc(s["title"])}</div><div class="ev-underline"></div>'
    elif kind=='connections':
        labels=s['labels'];xs=[140,470,795];ys=[170,75,170]
        content='<svg width="960" height="310" viewBox="0 0 960 310"><path class="ev-link" d="M140 155Q470 -20 795 155" fill="none" stroke="var(--gold)" stroke-width="4"/>'
        for label,x,y in zip(labels,xs,ys):content+=f'<text x="{x}" y="{y+25}" text-anchor="middle" font-family="Editorial" font-size="52" fill="var(--ink)">{esc(label)}</text>'
        content+=f'<text x="480" y="280" text-anchor="middle" font-family="Interface" font-size="32" fill="var(--muted)">{esc(s.get("copy",""))}</text></svg>'
        actions.append(f'tl.fromTo({js(selector+" .ev-link")},{{strokeDasharray:1100,strokeDashoffset:1100}},{{strokeDashoffset:0,duration:Math.min(.65,{duration}),ease:"power2.out"}},{a});')
    elif kind=='bar':
        ratio=100*s['value']/s['reference']
        content=f'<h2 class="ev-title" style="font-size:49px">{esc(s["title"])}</h2><div class="ev-bar"><div class="ev-fill" style="width:{ratio}%"></div><div class="ev-number">{esc(s.get("label",str(s["value"])))}</div></div><p class="ev-note">{esc(s["reference_label"])}</p>'
        actions.append(f'tl.fromTo({js(selector+" .ev-fill")},{{scaleX:0}},{{scaleX:1,duration:Math.min(.55,{duration}),ease:"power2.out"}},{a});')
    elif kind=='prototype':
        states=s['states'];content=''
        for i,state in enumerate(states):
            content+=f'<div class="ev-state" data-state="{esc(state["id"])}"><div class="ev-topline">{esc(state.get("label",""))}</div><h3>{esc(state["title"])}</h3><p>{esc(state.get("body",""))}</p>'
            if state.get('wireframe'):content+='<div class="ev-placeholder"></div>'
            if state.get('next'):content+=f'<button data-next="{esc(state["next"])}">{esc(state.get("button","Continuar"))} →</button>'
            content+='</div>'
        content=demo_frame(s,content)
        actions.append(f'''{{const root=document.querySelector({js(selector)}),states={js(states)};
 const show=id=>{{VideoDemos.navigate(states,id);root.querySelectorAll('[data-state]').forEach(el=>{{const active=el.dataset.state===id;el.style.opacity=active?1:0;el.style.pointerEvents=active?'auto':'none';}});}};
 root.querySelectorAll('[data-next]').forEach(el=>el.onclick=()=>show(el.dataset.next));
 const state={{t:0}},draw=()=>{{let selected=states[0];states.forEach(s=>{{if(state.t>=s.at)selected=s;}});show(selected.id);}};
 tl.fromTo(state,{{t:0}},{{t:{duration},duration:{duration},ease:'none',immediateRender:false,onUpdate:draw}},{a});draw();}}''')
    elif kind=='chronology':
        events=s['events'];content='<div class="ev-rail">'
        for e in events:content+=f'<button class="ev-event" data-event="{esc(e["id"])}"><small>{esc(e["date"])}</small>{esc(e["label"])}</button>'
        content+='</div>'
        for e in events:
            d=e['document'];content+=f'<div class="ev-doc" data-document="{esc(e["id"])}"><div class="ev-topline">{esc(d.get("label",e["date"]))}</div><h3>{esc(d["title"])}</h3><p>{esc(d["body"])}</p><a href="{esc(d["href"])}" target="_blank" rel="noopener">Abrir documento vinculado ↗</a></div>'
        content=demo_frame(s,content)
        actions.append(f'''{{const root=document.querySelector({js(selector)}),events={js(events)};
 const show=id=>{{VideoDemos.selectDocument(events,id);root.querySelectorAll('[data-document]').forEach(el=>{{const active=el.dataset.document===id;el.style.opacity=active?1:0;el.style.pointerEvents=active?'auto':'none';}});root.querySelectorAll('[data-event]').forEach(el=>el.classList.toggle('active',el.dataset.event===id));}};
 root.querySelectorAll('[data-event]').forEach(el=>el.onclick=()=>show(el.dataset.event));
 const state={{t:0}},draw=()=>{{let selected=events[0];events.forEach(e=>{{if(state.t>=e.at)selected=e;}});show(selected.id);}};
 tl.fromTo(state,{{t:0}},{{t:{duration},duration:{duration},ease:'none',immediateRender:false,onUpdate:draw}},{a});draw();}}''')
    elif kind=='pendulum':
        cfg=s.get('physics',{});L1=cfg.get('length_from',1);L2=cfg.get('length_to',2);g=cfg.get('gravity',9.81);change=cfg.get('change_at',duration/2);clock=cfg.get('clock_rate',1)
        content=demo_frame(s,'<svg width="480" height="540" viewBox="0 0 480 540"><path d="M110 75H370" stroke="var(--muted)" stroke-width="5"/><line class="ev-rope" x1="240" y1="75" stroke="var(--ink)" stroke-width="4"/><circle class="ev-bob" r="22" fill="var(--gold)"/></svg><div class="ev-measures">Comprimento<strong class="ev-length"></strong><input type="range" aria-label="Comprimento do pêndulo"><br>Período<strong class="ev-period"></strong><small>T = 2π√(L/g)<br>Pequenos ângulos</small></div>')
        actions.append(f'''{{const root=document.querySelector({js(selector)}),state={{t:0}},input=root.querySelector('input');let manual=null;
 input.min={min(L1,L2)};input.max={max(L1,L2)};input.step=.01;
 const draw=()=>{{const p=VideoDemos.pendulumState(state.t*{clock},{change}*{clock},{L1},{L2},{g});if(manual!==null){{p.length=manual;p.period=2*Math.PI*Math.sqrt(manual/{g});}}const len=300*p.length/{max(L1,L2)},x=240+len*Math.sin(p.angle),y=75+len*Math.cos(p.angle);root.querySelector('.ev-rope').setAttribute('x2',x);root.querySelector('.ev-rope').setAttribute('y2',y);root.querySelector('.ev-bob').setAttribute('cx',x);root.querySelector('.ev-bob').setAttribute('cy',y);root.querySelector('.ev-length').textContent=p.length.toFixed(1).replace('.',',')+' m';root.querySelector('.ev-period').textContent=p.period.toFixed(2).replace('.',',')+' s';input.value=p.length;}};
 input.oninput=()=>{{manual=Number(input.value);draw();}};
 tl.fromTo(state,{{t:0}},{{t:{duration},duration:{duration},ease:'none',immediateRender:false,onUpdate:()=>{{manual=null;draw();}}}},{a});draw();}}''')
    else:raise ValueError(f'Unknown scene type: {kind}')
    return content,actions
