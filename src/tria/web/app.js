'use strict';
const el = (id) => document.getElementById(id);
let currentStudy = null;
let currentAnalysis = null;
let analysesForStudy = [];
let busy = false;
const LABELS = {Pneumothorax:'Neumotórax',Effusion:'Derrame pleural',Consolidation:'Consolidación'};
const MAX_FILE = 12 * 1024 * 1024;

async function api(url, options) {
  const res = await fetch(url, options);
  let data;
  try { data = await res.json(); } catch { throw new Error('El servidor devolvió una respuesta no válida.'); }
  if (!res.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'Error HTTP ' + res.status);
  return data;
}
const itemText=(tag, value, cls) => {
  const node=document.createElement(tag);
  node.textContent=String(value);
  if(cls) node.className=cls;
  return node;
};
const dateFormat = str => {
  try { const d=new Date(str); return Number.isNaN(d.getTime())?str:d.toLocaleString('es-ES',{dateStyle:'short',timeStyle:'short'}); }
  catch { return str || ''; }
};
const short = (value) => String(value||'').slice(0,8);
function setStatus(message, kind='') {
  const view=el('progress'); view.textContent=message;view.className='status-line '+kind;
}
function setBusy(value, message) {
  busy=value;
  el('upload-button').disabled=value;
  el('analyse').disabled=value;
  for(const b of el('history').querySelectorAll('button')) b.disabled=value;
  if(message) setStatus(message, value?'busy':'');
}
function setSteps(stage) {
  ['step-upload','step-validate','step-analyse'].forEach((id,i) => {
    el(id).className='step'+(i<stage?' done':i===stage?' active':'');
  });
}
function appendRow(dl,label,value) {
  dl.appendChild(itemText('dt',label));
  dl.appendChild(itemText('dd',value));
}
function resetResult() {
  currentAnalysis=null;
  el('results').hidden=true;
  el('empty').hidden=false;
  el('heatmap-figure').hidden=true;
  el('heatmap').removeAttribute('src');
  el('analysis-select').replaceChildren();
  el('select-analysis').hidden=true;
}
function renderStudy(study) {
  currentStudy=study;
  el('study').hidden=false;
  el('study-label').textContent='ESTUDIO '+short(study.id).toUpperCase();
  el('preview').src='/api/v1/studies/'+encodeURIComponent(study.id)+'/preview';
  const dl=el('study-info'); dl.replaceChildren();
  appendRow(dl,'ID',study.id);
  appendRow(dl,'Formato',study.source_format);
  appendRow(dl,'Resolución',study.width+' × '+study.height+' píxeles');
  appendRow(dl,'SHA-256',study.sha256);
  const prov=study.provenance || {};
  if(prov.status==='coincidencia_sha256') appendRow(dl,'Procedencia',prov.label || 'Muestra NIH');
  if(prov.image_id) appendRow(dl,'Registro NIH',prov.image_id+' · '+prov.reference_label+' (etiqueta automática)');
  const tag=el('source-status');
  tag.textContent=prov.status==='coincidencia_sha256'?'Coincide con muestra NIH':'Origen no verificado';
  tag.className='source-pill'+(prov.status==='coincidencia_sha256'?' known':'');
  setSteps(2);
}
function addScore(container,label,value) {
  const row=itemText('div','','score-row');
  const head=itemText('div','','score-label');
  head.appendChild(itemText('span',label));
  head.appendChild(itemText('strong',(Number(value)*100).toFixed(1)+' %'));
  const track=itemText('div','','score-track');
  const fill=itemText('div','','score-fill');
  fill.style.width=Math.max(0,Math.min(100,Number(value)*100))+'%';
  track.appendChild(fill);row.append(head,track);container.appendChild(row);
}
function renderResult(analysis) {
  currentAnalysis=analysis;
  el('analysis-status').textContent=({EXPLORATORIO:'Análisis completado',DEMO_SIN_IA:'Prueba técnica',MODELO_NO_DISPONIBLE:'Modelo no disponible'})[analysis.status] || analysis.status;
  const showMessage=analysis.status==='MODELO_NO_DISPONIBLE';
  el('analysis-message').textContent=showMessage ? analysis.message : '';
  el('analysis-message').hidden=!showMessage;
  el('result-safety').hidden=analysis.status!=='EXPLORATORIO';
  const scores=el('scores'); scores.replaceChildren();
  const entries=Object.entries(analysis.scores||{});
  el('score-title').textContent=entries.length?'Puntuaciones del modelo':'Estadísticas de imagen';
  el('score-note').hidden=!entries.length;
  if(entries.length) {
    for(const [key, val] of entries) addScore(scores,LABELS[key]||key,val);
  } else {
    scores.appendChild(itemText('p','Prueba técnica: no se ha ejecutado el modelo de IA.','feature-row'));
  }
  for(const [k,v] of Object.entries(analysis.features||{})){
    scores.appendChild(itemText('p',k+': '+v,'feature-row'));
  }
  const showMap=!!analysis.heatmap_available;
  el('heatmap-figure').hidden=!showMap;
  if(showMap) {
    el('heatmap').src='/api/v1/analyses/'+encodeURIComponent(analysis.id)+'/heatmap';
    el('heatmap-target').textContent=analysis.gradcam_target ? 'Clase: '+(LABELS[analysis.gradcam_target]||analysis.gradcam_target) : 'Activación del modelo';
  } else {
    el('heatmap').removeAttribute('src');
  }
  el('report-link').href='/api/v1/analyses/'+encodeURIComponent(analysis.id)+'/report';
  el('results').hidden=false;el('empty').hidden=true;
  el('analysis-select').value=analysis.id;
  setSteps(3);
}
async function loadAnalyses(studyId) {
  analysesForStudy=await api('/api/v1/studies/'+encodeURIComponent(studyId)+'/analyses');
  const choose=el('analysis-select');choose.replaceChildren();
  for(const analysis of analysesForStudy) {
    const option=document.createElement('option');option.value=analysis.id;
    option.textContent=dateFormat(analysis.created_at)+' · '+analysis.status+' · '+short(analysis.id);
    choose.appendChild(option);
  }
  el('select-analysis').hidden=analysesForStudy.length<2;
  if(analysesForStudy.length) renderResult(analysesForStudy[0]);
  else resetResult();
}
async function openStudy(studyId) {
  if(busy) return;
  setBusy(true,'Recuperando estudio e historial…');
  try {
    const study=await api('/api/v1/studies/'+encodeURIComponent(studyId));
    renderStudy(study);
    await loadAnalyses(studyId);
    setStatus('Estudio recuperado. Puedes consultar sus informes anteriores.');
    for(const btn of el('history').querySelectorAll('button')) btn.classList.toggle('selected',btn.dataset.study===studyId);
    el('study').scrollIntoView({behavior:'smooth',block:'nearest'});
  } catch(e) {setStatus('Error al reabrir: '+e.message,'error');}
  finally {setBusy(false);}
}
async function reloadHistory() {
  const studies=await api('/api/v1/studies');
  const list=el('history');list.replaceChildren();
  if(!studies.length){list.appendChild(itemText('li','Todavía no hay estudios guardados.','history-empty'));return;}
  for(const study of studies){
    const li=document.createElement('li');
    const button=itemText('button','','history-button');button.type='button';button.dataset.study=study.id;
    if(currentStudy?.id===study.id)button.classList.add('selected');
    const left=itemText('div','');
    left.appendChild(itemText('div',dateFormat(study.created_at)+' · '+study.source_format,'name'));
    const prov=study.provenance||{};
    left.appendChild(itemText('div',prov.status==='coincidencia_sha256'?'Muestra NIH · '+prov.image_id+' · etiqueta: '+prov.reference_label:'Origen no verificado','meta'));
    button.append(left,itemText('span',short(study.id)+'  ↗','right'));
    button.addEventListener('click',()=>openStudy(study.id));
    li.appendChild(button);list.appendChild(li);
  }
}
async function refreshModel(){
  const info=await api('/api/v1/system');
  const isDemo=info.mode==='demo';
  el('model-info').textContent=isDemo?'Modo de pruebas · no ejecuta IA':'DenseNet-121 · modelo preentrenado';
  el('model-pill').textContent=isDemo?'PRUEBA · SIN IA':'IA · '+(info.model_loaded?'LISTA':'SE CARGARÁ AL ANALIZAR');
  el('analyse').firstChild.textContent=isDemo?'Ejecutar prueba técnica ':'Analizar con IA ';
  el('model-pill').dataset.mode=info.mode;
}

el('image-file').addEventListener('change',()=>{
  const f=el('image-file').files[0];el('filename').textContent=f?f.name:'Ningún archivo seleccionado';
  if(f && f.size>MAX_FILE)setStatus('Archivo superior a 12 MB. Elige otra imagen.','error');
});
const drop=el('drop-area');
for(const name of ['dragenter','dragover'])drop.addEventListener(name,e=>{e.preventDefault();drop.classList.add('dragging');});
for(const name of ['dragleave','drop'])drop.addEventListener(name,e=>{e.preventDefault();drop.classList.remove('dragging');});
drop.addEventListener('drop',e=>{
  if(!e.dataTransfer?.files?.length)return;
  el('image-file').files=e.dataTransfer.files;
  el('image-file').dispatchEvent(new Event('change',{bubbles:true}));
});
el('upload-form').addEventListener('submit',async e=>{
  e.preventDefault();if(busy)return;
  const file=el('image-file').files[0];if(!file)return;
  if(file.size>MAX_FILE){setStatus('Archivo superior a 12 MB.','error');return;}
  setBusy(true,'Validando formato, integridad y metadatos…');
  try{
    const payload=new FormData();payload.append('file',file);
    const study=await api('/api/v1/studies',{method:'POST',body:payload});
    renderStudy(study);resetResult();setSteps(2);
    analysesForStudy=[];
    setStatus('Imagen aceptada y registrada.');
    await reloadHistory();
  }catch(err){setStatus('No se pudo cargar la imagen: '+err.message,'error');}
  finally{setBusy(false);}
});
el('analyse').addEventListener('click',async()=>{
  if(busy||!currentStudy)return;
  setBusy(true,'Analizando imagen… La primera carga del modelo puede tardar.');
  try {
    const analysis=await api('/api/v1/studies/'+encodeURIComponent(currentStudy.id)+'/analyses',{method:'POST'});
    await loadAnalyses(currentStudy.id);
    renderResult(analysis);
    setStatus('Ejecución registrada.');
    await refreshModel();
  }catch(err){setStatus('No se pudo ejecutar: '+err.message,'error');}
  finally{setBusy(false);}
});
el('copy-hash').addEventListener('click',async()=>{
  if(!currentStudy)return;
  try{await navigator.clipboard.writeText(currentStudy.sha256);setStatus('SHA-256 copiado al portapapeles.');}
  catch{setStatus('No se pudo copiar. Selecciona el SHA-256 en la ficha del estudio.','error');}
});
el('analysis-select').addEventListener('change',async e=>{
  const found=analysesForStudy.find(x=>x.id===e.target.value);
  if(found)renderResult(found);
});
el('refresh-history').addEventListener('click',()=>reloadHistory().then(()=>setStatus('Historial actualizado.')).catch(err=>setStatus(err.message,'error')));
refreshModel().catch(err=>{el('model-info').textContent='Motor no disponible: '+err.message;el('model-pill').textContent='SIN CONEXIÓN';});
reloadHistory().catch(err=>{el('history').replaceChildren(itemText('li','Error al cargar historial: '+err.message,'history-empty'));});
