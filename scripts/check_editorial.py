#!/usr/bin/env python3
"""Behavioral checks plus an optional 28-second local render fixture.
Never modifies the approved benchmark or an existing delivery.
"""
import argparse
import copy
import json
from pathlib import Path
from video_pipeline import SKILL, run, write
from editorial_pipeline import EditorialProject
from retime_project import transform_component, retime


def check(output,render=False):
    root=Path(output).resolve()
    if root.exists():raise ValueError('Choose a new QA directory')
    root.mkdir(parents=True);benchmark=SKILL/'assets/benchmark';data=json.loads((benchmark/'project.json').read_text())
    for c in data['components'].values():
        c['master']=str(benchmark/c['master']);c['captions']=str(benchmark/c['captions']);c['evidence']=[]
    for a in data['assets'].values():a['file']=str(benchmark/a['file'])
    data['editorial']={'sounds':{'tap':{'file':'tap.wav','source':'Generated QA sine tone','license':'Generated locally for test','duration':.12,'peak_dbfs':-28}}}
    run(['ffmpeg','-y','-v','error','-f','lavfi','-i','sine=frequency=600:duration=0.12','-ar','48000','-ac','2',root/'tap.wav'])
    run(['ffmpeg','-y','-v','error','-f','lavfi','-i','sine=frequency=130:duration=2','-af','volume=0.03','-ar','48000','-ac','2',root/'music.wav'])
    data['music']={'file':'music.wav','gain':1}
    for n in [1,2]:write(root/f'doc{n}.html',f'<!doctype html><html lang="pt"><meta charset="utf-8"><h1>Documento fictício {n}</h1><p>Arquivo de teste vinculado a um acontecimento.</p></html>')
    c=data['components']['01_principal'];c['shift_y']=0;c['demo_crop']=[160,600,920,1730];c['caption_highlights']=['inteligência','matemática'];c['scenes']=[
        {'type':'title','start':.1,'end':1.1,'title':'Uma ideia, um caminho.'},
        {'type':'image','start':1.2,'end':3.2,'asset':'datacenter','title':'Imagem única','credit':'Carl Lender · CC BY 2.0'},
        {'type':'connections','start':3.3,'end':4.4,'labels':['Ideia','Teste','Resultado'],'copy':'Conectar conhecimentos.'},
        {'type':'bar','start':4.5,'end':5.7,'title':'Medida de exemplo','value':72,'reference':100,'reference_label':'100 pontos = referência fictícia'},
        {'type':'prototype','start':6,'end':9,'title':'Um fluxo que funciona.','footer':'Do esboço\nao resultado.','copy':'Dados fictícios para demonstração.','states':[{'id':'a','at':0,'title':'Explore uma ideia.','wireframe':True,'next':'b','button':'Abrir resultado'},{'id':'b','at':1.5,'title':'Resultado disponível.','body':'A ação leva à próxima tela.','next':'a','button':'Voltar'}]},
        {'type':'pendulum','start':9,'end':12,'title':'Mude e observe.','footer':'Comprimento\ne período.','physics':{'length_from':1,'length_to':2,'change_at':1.5}},
        {'type':'chronology','start':12,'end':16.5,'title':'Cada fato, sua fonte.','footer':'Documentos\nconectados.','events':[{'id':'a','at':0,'date':'01 jun','label':'Solicitação','document':{'title':'Pedido inicial','body':'Documento fictício para teste.','href':'doc1.html'}},{'id':'b','at':2.2,'date':'08 jun','label':'Entrega','document':{'title':'Comprovante','body':'Arquivo vinculado à entrega.','href':'doc2.html'}}]}
    ];c['sfx']=[{'sound':'tap','start':7.5}];c['music_duck']=[{'start':12,'end':16.5,'gain':.3}]
    data['components']['05_superpotencia']['framing']={'scale':1.1,'origin':[.5,.8]}
    project=root/'project.json';write(project,data);p=EditorialProject(project);p.validate();passed=['valid multi-scene project']
    def rejects(change,label):
        bad=copy.deepcopy(data);change(bad);write(root/'bad.json',bad)
        try:EditorialProject(root/'bad.json').validate(media=False)
        except (ValueError,KeyError):passed.append(label)
        else:raise AssertionError(label)
    rejects(lambda d:d['components']['01_principal']['scenes'][0].update(rect=[60,600,1000,1400]) or d['components']['01_principal'].update(face_bounds=[260,610,840,1300]),'face obstruction rejected')
    rejects(lambda d:d['components']['01_principal']['scenes'][4]['states'][0].update(next='missing'),'broken prototype link rejected')
    rejects(lambda d:d['components']['01_principal']['scenes'][6]['events'][0]['document'].update(href='missing.pdf'),'missing document rejected')
    rejects(lambda d:d['components']['01_principal']['sfx'][0].update(start=90),'SFX outside duration rejected')
    rejects(lambda d:d['components']['01_principal']['scenes'][1].update(start=.5),'overlapping scenes rejected')
    rejects(lambda d:d['components']['01_principal']['scenes'][5]['physics'].update(length_to=0),'invalid physics rejected')
    old={'frames':180,'scenes':[{'type':'prototype','start':1,'end':5,'states':[{'at':0},{'at':2}]}],'sfx':[{'sound':'tap','start':3}],'music_duck':[{'start':4,'end':5,'gain':.3}]}
    cues=[{'start':.6,'end':5.5,'text':'Frase de teste','words':[{'start':.6,'end':.9,'word':'Frase'},{'start':1,'end':1.2,'word':'de'},{'start':1.3,'end':1.8,'word':'teste'}]}]
    changed,caps=transform_component(old,cues,15,0,1.1)
    assert changed['frames']==150 and abs(changed['sfx'][0]['start']-2.5/1.1)<1e-9 and changed['scenes'][0]['states'][1]['at']==2/1.1 and caps[0]['words'][0]['start']>0
    passed.append('one map shifts cut, speed, words, scenes, local states, SFX and ducking')
    try:transform_component(old,cues,21)
    except ValueError:passed.append('cut into spoken word rejected')
    else:raise AssertionError('Speech cut not rejected')
    runtime=SKILL/'assets/editorial/demo_runtime.js'
    out=run(['node','-e',f"const m=require({json.dumps(str(runtime))});const a=m.pendulumState(0,3,1,2),b=m.pendulumState(4,3,1,2);if(Math.abs(b.period/a.period-Math.sqrt(2))>1e-10)throw Error('period');const x=m.navigate([{{id:'a'}},{{id:'b'}}],'b');if(x.id!=='b')throw Error('navigation');if(m.selectDocument([{{id:'x',document:{{title:'Yes'}}}}],'x').title!=='Yes')throw Error('document');console.log('models OK')"])
    passed.append(out.strip())
    built=p.build();oldkey=built['05_superpotencia']['fingerprint'];data['components']['05_superpotencia']['framing']['scale']=1.11;write(project,data);newkey=EditorialProject(project).build()['05_superpotencia']['fingerprint'];assert oldkey!=newkey;passed.append('zoom change invalidates cache');data['components']['05_superpotencia']['framing']['scale']=1.1;write(project,data)
    # Real FFmpeg retime: verify exact frame count/audio duration and sidecar map.
    short={'schema_version':2,'output':'build','components':{'clip':{'frames':60,'master':'short.mp4','captions':'short.json'}},'variants':[{'id':'clip','components':['clip']}]}
    run(['ffmpeg','-y','-v','error','-f','lavfi','-i','color=c=white:s=1080x1920:r=30:d=2','-f','lavfi','-i','sine=frequency=440:duration=2','-vf','format=yuv420p','-c:v','libx264','-preset','ultrafast','-c:a','aac','-ar','48000','-ac','2','-t','2',root/'short.mp4'])
    write(root/'short.json',[{'start':.6,'end':1.7,'text':'Teste de corte','words':[{'word':'Teste','start':.6,'end':.9}]}]);write(root/'short-project.json',short)
    dest=retime(root/'short-project.json',root/'retimed',['clip'],15,0,1.1,'Synthetic synchronization fixture');from video_pipeline import probe,stream
    actual=json.loads(dest.read_text());info=probe(dest.parent/actual['components']['clip']['master']);assert int(stream(info,'video')['nb_frames'])==41 and abs(float(stream(info,'audio')['duration'])-41/30)<.003;passed.append('FFmpeg retime exact frames and audio duration')
    if render:
        p=EditorialProject(project);p.render();p.verify();built=json.loads((p.out/'build.json').read_text())['components']
        run(['npx','--yes','hyperframes@0.8.33','snapshot',built['01_principal']['folder'],'--at','.5,2,3.8,5.2,6.5,8.5,9.5,11.5,12.5,15.5','--no-end','--output',root/'frames'])
        passed.append('full render, decode, assembly and ten scene snapshots')
    write(root/'checks.json',{'ok':True,'checks':passed});print(json.dumps(passed,ensure_ascii=False,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True);p.add_argument('--render',action='store_true');a=p.parse_args();check(a.output,a.render)
