"""Coach 3D articulé : rendu Three.js avec repli si WebGL indisponible."""
import json
import re
import streamlit.components.v1 as components


def _kind(name):
    n = name.lower()
    for words, kind in [
        (('pompe', 'push-up'), 'pushup'), (('squat', 'chaise'), 'squat'),
        (('fente', 'lunge'), 'lunge'), (('burpee',), 'burpee'),
        (('mountain', 'grimpeur'), 'mountain'), (('gainage', 'planche', 'plank'), 'plank'),
        (('jumping jack',), 'jumping'), (('abdo', 'crunch'), 'crunch'),
        (('course', 'marche', 'jogging', 'genou'), 'run'),
    ]:
        if any(w in n for w in words): return kind
    return 'general'


def show(exercises, work=30, rest=45):
    data = []
    rounds = max((max(1, min(int(ex.get('sets', 1)), 20)) for ex in exercises), default=0)
    # Ordre en circuit : exercice 1, 2, 3... puis tour suivant.
    for i in range(rounds):
        for ex in exercises:
            unit = str(ex.get('unit', 'rep'))
            sets = max(1, min(int(ex.get('sets', 1)), 20))
            if i >= sets:
                continue
            targets = ex.get('targets') or []
            count = int(targets[i] if i < len(targets) else ex.get('count', 10))
            data.append({'name': str(ex.get('name', 'Exercice'))[:100], 'kind': _kind(str(ex.get('name', ''))),
                         'count': count, 'unit': unit, 'set': i + 1, 'sets': sets,
                         'duration': max(5, min(count if unit == 'sec' else int(work), 600)),
                         'rest': max(0, min(int(rest), 120))})
    if not data:
        return
    html = TEMPLATE.replace('__DATA__', json.dumps(data, ensure_ascii=False).replace('<', '\\u003c'))
    components.html(html, height=980, scrolling=True)


def show_free_plan(plan, difficulty='Intermédiaire', work=45, rest=30):
    """Réutilise le coach animé de la séance guidée, dans l'ordre exact du circuit libre."""
    data = []
    for ex in plan:
        name = str(ex.get('name', 'Exercice'))
        target = str(ex.get('target', ''))
        match = re.search(r'(\d+)', target)
        amount = int(match.group(1)) if match else 10
        timed = 'seconde' in target.lower()
        data.append({
            'name': name[:100], 'kind': _kind(name),
            'count': amount, 'unit': 'sec' if timed else 'rep',
            'set': int(ex.get('tour', 1)),
            'sets': max(1, max(int(item.get('tour', 1)) for item in plan)),
            'duration': max(5, min(amount if timed else int(work), 600)),
            'rest': max(0, min(int(rest), 120)),
        })
    if not data:
        return
    html = TEMPLATE.replace('__DATA__', json.dumps(data, ensure_ascii=False).replace('<', '\u003c'))
    # Identité Gotham pour le coach libre sans modifier le coach guidé.
    html = html.replace('background:#fff;border:1px solid #e8d7df', 'background:#101a26;border:1px solid #b58b2d')
    html = html.replace('color:#351627', 'color:#f5d16b')
    html = html.replace('background:#fff8fa,#f8edf1', 'background:#101a26,#192435')
    html = html.replace('background:#832746', 'background:#b58b2d')
    html = html.replace('color:white;padding:12px', 'color:#0c121b;padding:12px')
    html = html.replace('background:#f2e7ec;color:#752440', 'background:#243449;color:#f5d16b')
    html = html.replace('color:#812443', 'color:#f5c542')
    html = html.replace('color:#782343', 'color:#f5c542')
    html = html.replace('background:#fff9', 'background:#101a26dd')
    html = html.replace('color:#822645', 'color:#f5c542')
    components.html(html, height=980, scrolling=True)


TEMPLATE = r'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>
*{box-sizing:border-box}body{margin:0;background:transparent;font:15px system-ui,sans-serif;color:#351627}.coach{background:#101a26;border:1px solid #b58b2d;border-radius:20px;padding:18px;max-width:1100px;margin:auto}.top,.actions,.options{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap}.tag{background:#f4e3e9;color:#7e2545;border-radius:20px;padding:7px 12px;font-weight:700;font-size:12px}h2{margin:12px 0 4px;font-size:25px}.sub{color:#765b67}.scene{position:relative;margin:12px 0;background:linear-gradient(125deg,#fff8fa,#f8edf1);border-radius:16px;overflow:hidden;height:330px}.scene svg{height:100%;width:100%}.floor{stroke:#c5a0af;stroke-width:3;stroke-linecap:round}.limb{stroke:#842748;stroke-width:12;stroke-linecap:round;stroke-linejoin:round;fill:none}.torso{stroke:#a63758;stroke-width:19;stroke-linecap:round}.head{fill:#efb49e;stroke:#722340;stroke-width:3}.scene-label{position:absolute;bottom:10px;left:0;right:0;text-align:center;font-weight:750;color:#782343}.countdown{position:absolute;inset:0;background:#fff9;display:none;align-items:center;justify-content:center;font-size:105px;font-weight:900;color:#822645}.countdown.visible{display:flex}.advice{background:#fff1f5;border-left:4px solid #a6365a;padding:12px;border-radius:8px}.phase{text-align:center;font-weight:800;letter-spacing:1px;margin-top:12px}.clock{text-align:center;font-size:55px;font-weight:850;color:#812443;font-variant-numeric:tabular-nums}.bar{height:9px;background:#f1e1e7;border-radius:20px;overflow:hidden}.fill{height:100%;background:#a63359;width:0}.actions{justify-content:center;margin:13px 0}.actions button{background:#832746;border:0;border-radius:11px;color:white;padding:12px 15px;font-weight:750;min-height:44px;cursor:pointer}.actions button.alt{background:#f2e7ec;color:#752440}.actions button:disabled{opacity:.45}.options{justify-content:center;margin:10px}.status{text-align:center;min-height:22px;font-size:13px;color:#75465a}.next{font-weight:650;color:#8d3151;margin:8px 0}.summary{display:none;background:#f9eaf0;padding:15px;border-radius:12px}.summary.visible{display:block}.note{text-align:center;font-size:12px;color:#775c68}.coach:fullscreen{background:white;overflow:auto;height:100vh}.coach:fullscreen .scene{height:min(53vh,540px)}@media(max-width:550px){.coach{padding:10px}.scene{height:250px}.clock{font-size:46px}.actions{gap:6px}.actions button{padding:10px}}
</style></head><body><div class="coach" id="coach"><div class="top"><span class="tag" id="position"></span><span class="tag" id="set"></span></div><h2 id="name"></h2><div class="sub" id="detail"></div><div class="scene"><div id="three-stage" style="width:100%;height:100%"></div><div class="scene-label" id="movement"></div><div class="countdown" id="countdown">3</div></div><div class="advice" id="advice"></div><div class="next" id="nextup"></div><div class="phase" id="phase">PRÊT</div><div class="clock" id="clock">00:30</div><div class="bar"><div class="fill" id="fill"></div></div><div class="actions"><button class="alt" id="test">🔊 Tester la voix</button><button id="start">▶ Démarrer</button><button class="alt" id="pause">⏸ Pause</button><button class="alt" id="next">⏭ Suivant</button><button class="alt" id="reset">↺ Recommencer</button><button class="alt" id="full">⛶ Plein écran</button></div><div class="options"><label><input type="checkbox" id="beep" checked> Bips</label><label><input type="checkbox" id="voice" checked> Coach vocal</label><label><input type="checkbox" id="auto" checked> Enchaînement auto</label></div><div class="status" id="status" role="status"></div><div class="summary" id="summary"></div><p class="note">Démonstrations 3D indicatives : elles ne vérifient pas ta posture. Arrête en cas de douleur, malaise ou vertige. Les annonces peuvent interrompre la musique.</p></div><script>
const exercises=__DATA__,$=id=>document.getElementById(id);let idx=0,mode='ready',remain=0,deadline=0,running=false,loop=null,elapsed=0,completed=0,lastTick=0,said10=false,audio=null,chosenVoice=null;
// Chaque position contient tête, épaules, hanches, coudes, mains, genoux et pieds : véritables articulations interpolées.
const P={
stand:[[200,49],[200,80],[200,145],[170,112],[162,143],[230,112],[238,143],[182,181],[182,222],[218,181],[218,222]],
squat:[[200,95],[200,126],[200,165],[167,140],[150,165],[233,140],[250,165],[155,182],[150,222],[245,182],[250,222]],
lunge:[[200,65],[200,97],[200,145],[173,117],[167,148],[227,117],[233,148],[245,182],[277,222],[151,189],[117,222]],
pushupTop:[[105,143],[124,156],[235,158],[120,183],[121,221],[226,183],[226,221],[278,179],[318,221],[280,179],[324,221]],
pushupDown:[[105,181],[124,192],[235,195],[120,202],[121,221],[226,202],[226,221],[278,207],[318,221],[280,207],[324,221]],
plank:[[105,160],[124,170],[235,170],[118,195],[117,222],[228,195],[227,222],[278,192],[318,222],[280,192],[324,222]],
mountainL:[[105,160],[124,170],[235,170],[118,195],[117,222],[228,195],[227,222],[265,194],[227,222],[280,192],[324,222]],
mountainR:[[105,160],[124,170],[235,170],[118,195],[117,222],[228,195],[227,222],[278,192],[318,222],[250,193],[212,222]],
jump:[[200,55],[200,86],[200,143],[164,71],[140,33],[236,71],[260,33],[161,182],[142,222],[239,182],[258,222]],
runL:[[200,49],[200,80],[200,145],[172,103],[160,80],[230,115],[244,138],[174,169],[150,212],[229,174],[260,197]],
runR:[[200,49],[200,80],[200,145],[172,115],[160,138],[230,103],[244,80],[174,174],[143,197],[229,169],[260,212]],
crunchDown:[[105,182],[139,188],[209,190],[141,173],[158,161],[174,173],[188,161],[249,190],[272,221],[252,190],[283,221]],
crunchUp:[[140,130],[162,151],[209,190],[151,138],[167,126],[184,138],[199,126],[249,190],[272,221],[252,190],[283,221]]};
const sequences={squat:['stand','squat','stand'],pushup:['pushupTop','pushupDown','pushupTop'],plank:['plank'],lunge:['stand','lunge','stand'],burpee:['stand','squat','plank','pushupDown','plank','squat','jump','stand'],mountain:['mountainL','mountainR'],jumping:['stand','jump','stand'],run:['runL','runR'],crunch:['crunchDown','crunchUp','crunchDown'],general:['stand','squat','stand']};
const labels={stand:'Position de départ',squat:'Descends en fléchissant les genoux',lunge:'Fléchis les jambes',pushupTop:'Bras tendus · corps aligné',pushupDown:'Descends en fléchissant les bras',plank:'Maintiens la planche',mountainL:'Ramène le genou gauche',mountainR:'Ramène le genou droit',jump:'Saute ou monte sur la pointe des pieds',runL:'Monte le genou',runR:'Alterne les jambes',crunchDown:'Position au sol',crunchUp:'Relève légèrement le buste'};
const tips={squat:'Pieds stables, hanches vers l’arrière, genoux alignés.',pushup:'Corps gainé, plie les coudes puis repousse le sol.',plank:'Garde le bassin stable et respire normalement.',lunge:'Buste droit, descends sans précipitation.',burpee:'Debout → accroupi → planche → retour debout. Saute seulement si confortable.',mountain:'Mains sous les épaules, alterne les genoux sans rebond.',jumping:'Écarte bras et jambes puis reviens, sans impact si nécessaire.',run:'Garde un rythme contrôlé et une respiration régulière.',crunch:'Ne tire pas sur la nuque.',general:'Contrôle ta respiration et ton amplitude.'};
function lerp(a,b,t){return a+(b-a)*t}function smooth(t){return t*t*(3-2*t)}function current(){return exercises[idx]}function fmt(s){s=Math.max(0,Math.ceil(s));return String(Math.floor(s/60)).padStart(2,'0')+':'+String(s%60).padStart(2,'0')}
function draw(now){const ex=current();if(!ex)return;const seq=sequences[ex.kind]||sequences.general;let rate=ex.kind==='burpee'?950:ex.kind==='plank'?1000:ex.kind==='mountain'||ex.kind==='run'?520:850;let phase=running&&mode==='work'?now/rate:0;let i=Math.floor(phase)%seq.length,t=smooth(phase-Math.floor(phase));if(seq.length===1){i=0;t=0}const a=P[seq[i]],b=P[seq[(i+1)%seq.length]],pts=a.map((p,k)=>[lerp(p[0],b[k][0],t),lerp(p[1],b[k][1],t)]);if(window.updateCoach3D)window.updateCoach3D(pts,ex.kind);$('movement').textContent=mode==='rest'?'Récupération':labels[seq[i]]||'Mouvement contrôlé';}
function voices(){return 'speechSynthesis'in window?window.speechSynthesis.getVoices():[]}function voiceSelect(){chosenVoice=voices().find(v=>/^fr(-|_)/i.test(v.lang))||voices().find(v=>/^fr/i.test(v.lang))||null}function speak(text,test=false){if(!test&&!$('voice').checked)return;if(!('speechSynthesis'in window)){$('status').textContent='Synthèse vocale indisponible : les bips restent utilisables.';return}try{speechSynthesis.cancel();let u=new SpeechSynthesisUtterance(text);u.lang='fr-FR';u.rate=.96;u.volume=1;if(chosenVoice)u.voice=chosenVoice;u.onstart=()=>{$('status').textContent='🔊 Coach vocal actif'};u.onerror=e=>{$('status').textContent='Voix indisponible ('+e.error+'). Vérifie les voix système et le son du navigateur.'};speechSynthesis.speak(u)}catch(e){$('status').textContent='Erreur vocale : '+e.message}}
function unlock(){try{let C=window.AudioContext||window.webkitAudioContext;if(C&&!audio)audio=new C();if(audio&&audio.state==='suspended')audio.resume()}catch(e){}}function beep(f=720){if(!$('beep').checked)return;try{unlock();if(!audio)return;let o=audio.createOscillator(),g=audio.createGain();o.connect(g);g.connect(audio.destination);o.frequency.value=f;g.gain.setValueAtTime(.0001,audio.currentTime);g.gain.exponentialRampToValueAtTime(.06,audio.currentTime+.02);g.gain.exponentialRampToValueAtTime(.0001,audio.currentTime+.19);o.start();o.stop(audio.currentTime+.2)}catch(e){}}
function render(){let e=current();$('name').textContent=e?e.name:'Séance terminée';$('position').textContent='Exercice '+Math.min(idx+1,exercises.length)+' / '+exercises.length;$('set').textContent=e?'Série '+e.set+' / '+e.sets:'Terminé';$('detail').textContent=e?(e.duration+' s d’effort · '+e.rest+' s de récupération'):'';$('advice').textContent=tips[e?.kind]||tips.general;$('nextup').textContent=idx+1<exercises.length?'Ensuite : '+exercises[idx+1].name:'';$('phase').textContent={ready:'PRÊT',prep:'PRÉPARATION',work:'🔥 EFFORT',rest:'💧 RÉCUPÉRATION',done:'🏆 TERMINÉ'}[mode];$('clock').textContent=fmt(remain);$('countdown').classList.toggle('visible',mode==='prep');$('countdown').textContent=Math.max(1,Math.ceil(remain));let total=mode==='prep'?3:mode==='rest'?(e?.rest||1):(e?.duration||1);$('fill').style.width=(mode==='done'?100:Math.max(0,Math.min(100,100*(1-remain/total))))+'%';$('start').disabled=running||mode==='done';$('start').textContent=mode==='ready'?'▶ Démarrer':'▶ Reprendre';$('pause').disabled=!running;$('next').disabled=mode==='done'}
function halt(){if(running)remain=Math.max(0,(deadline-performance.now())/1000);running=false;if(loop){cancelAnimationFrame(loop);loop=null}render()}
function setPhase(m,s){mode=m;remain=s;said10=false;render()}
function next(auto=false){if(!auto)halt();idx++;if(idx>=exercises.length){setPhase('done',0);$('summary').classList.add('visible');$('summary').textContent='🏆 Bravo ! '+completed+' séries terminées · '+Math.round(elapsed/60)+' min d’effort. Enregistre ton ressenti sous le coach.';beep(920);speak('Bravo ! Séance terminée !');running=false;return}setPhase('prep',3);beep();speak('Prépare-toi pour '+current().name);if(!auto&&$('auto').checked)startClock()}
function advance(){if(mode==='prep'){setPhase('work',current().duration);beep(840);speak('C’est parti ! '+current().name)}else if(mode==='work'){completed++;if(current().rest>0&&idx<exercises.length-1){setPhase('rest',current().rest);beep(540);speak('Récupération. Respire.')}else next(true)}else if(mode==='rest')next(true)}
function frame(now){if(!running)return;let delta=Math.max(0,Math.min((now-lastTick)/1000,.25));lastTick=now;remain=Math.max(0,(deadline-now)/1000);if(mode==='work'){elapsed+=delta;if(remain<=10&&!said10){said10=true;speak('Encore dix secondes !')}}if(remain<=0){advance();deadline=now+remain*1000;if(mode==='done'){render();return}if(!$('auto').checked){halt();return}}render();draw(now);loop=requestAnimationFrame(frame)}
function startClock(){if(running)return;unlock();running=true;lastTick=performance.now();deadline=lastTick+remain*1000;loop=requestAnimationFrame(frame);render()}
$('start').onclick=()=>{unlock();voiceSelect();if(mode==='ready'){setPhase('prep',3);speak('Prépare-toi pour '+current().name)}startClock()};$('pause').onclick=()=>{halt();if('speechSynthesis'in window)speechSynthesis.cancel()};$('next').onclick=()=>{unlock();next(false)};$('reset').onclick=()=>{halt();idx=0;completed=0;elapsed=0;$('summary').classList.remove('visible');setPhase('ready',current().duration);draw(0)};$('test').onclick=()=>{unlock();voiceSelect();$('voice').checked=true;$('status').textContent=chosenVoice?'Test de la voix française en cours…':'Aucune voix française détectée : essai avec la voix système.';speak('Bonjour ! Je suis ton coach Fit Evolution. Prépare-toi à bouger !',true)};$('full').onclick=()=>{let c=$('coach');if(document.fullscreenElement)document.exitFullscreen();else if(c.requestFullscreen)c.requestFullscreen()};$('voice').onchange=()=>{if(!$('voice').checked&&'speechSynthesis'in window)speechSynthesis.cancel()};if('speechSynthesis'in window){speechSynthesis.getVoices();speechSynthesis.addEventListener('voiceschanged',voiceSelect);voiceSelect()}
setPhase('ready',current().duration);draw(0);
</script><script src="https://cdn.jsdelivr.net/npm/three@0.152.2/build/three.min.js"></script><script>
(function(){
const mount=document.getElementById('three-stage');
if(!window.THREE){mount.innerHTML='<p style="padding:30px;text-align:center">Le coach 3D nécessite une connexion pour charger le moteur graphique Three.js.</p>';return;}
try{
const scene=new THREE.Scene();scene.background=new THREE.Color(0xf7edf2);
const camera=new THREE.PerspectiveCamera(37,1,.1,100);camera.position.set(0,1.5,7.8);camera.lookAt(0,1.3,0);
const renderer=new THREE.WebGLRenderer({antialias:true,alpha:false});renderer.setPixelRatio(Math.min(devicePixelRatio,2));mount.appendChild(renderer.domElement);
scene.add(new THREE.HemisphereLight(0xffffff,0xb3a3a6,2.1));const light=new THREE.DirectionalLight(0xffffff,2.1);light.position.set(-3,6,5);scene.add(light);
const matSkin=new THREE.MeshStandardMaterial({color:0xc88d70,roughness:.8});const matShirt=new THREE.MeshStandardMaterial({color:0x823557,roughness:.85});const matShort=new THREE.MeshStandardMaterial({color:0x262c43,roughness:.9});const matShoe=new THREE.MeshStandardMaterial({color:0xfafafa,roughness:.65});
const floor=new THREE.Mesh(new THREE.PlaneGeometry(12,12),new THREE.MeshStandardMaterial({color:0xe8d9df,roughness:1}));floor.rotation.x=-Math.PI/2;floor.position.y=-.05;scene.add(floor);
const sphere=new THREE.SphereGeometry(1,20,14);function ball(r,mat){let m=new THREE.Mesh(sphere,mat);m.scale.setScalar(r);scene.add(m);return m}
function segment(radius,mat){let m=new THREE.Mesh(new THREE.CylinderGeometry(radius*.87,radius,1,12),mat);scene.add(m);return m}
const head=ball(.23,matSkin),neck=segment(.09,matSkin),torso=segment(.27,matShirt),pelvis=ball(.22,matShort);
const arms=[segment(.115,matShirt),segment(.09,matSkin),segment(.115,matShirt),segment(.09,matSkin)];
const legs=[segment(.17,matShort),segment(.115,matSkin),segment(.17,matShort),segment(.115,matSkin)];
const hands=[ball(.105,matSkin),ball(.105,matSkin)],feet=[ball(.14,matShoe),ball(.14,matShoe)];
const joints=[ball(.115,matShirt),ball(.115,matShirt),ball(.14,matShort),ball(.14,matShort)];
const axis=new THREE.Vector3(0,1,0);function between(mesh,a,b){const d=new THREE.Vector3().subVectors(b,a);mesh.position.copy(a).addScaledVector(d,.5);mesh.scale.y=d.length();mesh.quaternion.setFromUnitVectors(axis,d.normalize())}
function point(p,side=0){return new THREE.Vector3((p[0]-200)/78,Math.max(.09,(222-p[1])/78),side)}
window.updateCoach3D=function(p){let v=p.map((q,i)=>point(q,i===3||i===4||i===7||i===8?-.16:i===5||i===6||i===9||i===10?.16:0));head.position.copy(v[0]);head.position.y+=.09;between(neck,v[0],v[1]);between(torso,v[1],v[2]);pelvis.position.copy(v[2]);
[[1,3],[3,4],[1,5],[5,6]].forEach((ab,i)=>between(arms[i],v[ab[0]],v[ab[1]]));[[2,7],[7,8],[2,9],[9,10]].forEach((ab,i)=>between(legs[i],v[ab[0]],v[ab[1]]));hands[0].position.copy(v[4]);hands[1].position.copy(v[6]);feet[0].position.copy(v[8]);feet[1].position.copy(v[10]);[3,5,7,9].forEach((id,i)=>joints[i].position.copy(v[id]));};
function resize(){let w=mount.clientWidth||400,h=mount.clientHeight||330;camera.aspect=w/h;camera.updateProjectionMatrix();renderer.setSize(w,h)}new ResizeObserver(resize).observe(mount);resize();if(typeof draw === "function")draw(0);
(function animate(){requestAnimationFrame(animate);renderer.render(scene,camera)})();
}catch(err){mount.textContent='Impossible de lancer le rendu 3D : '+err.message}
})();
</script></body></html>'''
