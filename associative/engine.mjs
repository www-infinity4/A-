import {createHash} from 'node:crypto';
const hash=s=>createHash('sha256').update(s).digest('hex');
const lower=s=>s.normalize('NFC').toLowerCase();
function grams(s){const a=Array.from(lower(s)),m=new Map();for(const n of [2,3,4])for(let i=0;i+n<=a.length;i++){const g=a.slice(i,i+n).join('');m.set(g,(m.get(g)||0)+1);}return m;}
function cosine(a,b){let dot=0,x=0,y=0;for(const [k,v] of a){dot+=v*(b.get(k)||0);x+=v*v;}for(const v of b.values())y+=v*v;return x&&y?dot/Math.sqrt(x*y):0;}
const includes=(text,term)=>lower(text).includes(lower(term));
export function buildIndex(blocks,{projects=[],wiring=[],symbols={}}={}){
 if(!Array.isArray(blocks)||blocks.length>10000||blocks.some(b=>typeof b!=='string'||b.length>200000))throw Error('block limit');
 if(!Array.isArray(projects)||projects.length>256||projects.some(p=>typeof p!=='string'||!p.trim())||new Set(projects).size!==projects.length)throw Error('project invalid');
 const graph=new Map(projects.map(p=>[p,new Set()]));
 for(const [a,b] of wiring){if(!graph.has(a)||!graph.has(b))throw Error('wiring invalid');graph.get(a).add(b);graph.get(b).add(a);}
 const legend=Object.entries(symbols);if(legend.length>128||legend.some(([s,t])=>!s||typeof t!=='string'||!t.trim()))throw Error('symbol invalid');
 const seen=new Map();for(const [i,text] of blocks.entries()){if(!text.trim())continue;const id=hash(text);if(seen.has(id)){seen.get(id).origins.push(i);continue;}seen.set(id,{id,text,origins:[i],grams:grams(text),projects:projects.filter(p=>includes(text,p)),symbols:legend.filter(([s])=>text.includes(s)).map(([s])=>s)});}
 return {nodes:[...seen.values()],graph,legend};
}
export function rank(model,query,{weights={}}={}){
 if(typeof query!=='string'||query.length>8192)throw Error('query limit');
 const w={character:0.45,project:0.4,symbol:0.15,...weights};if(Object.keys(w).some(k=>!['character','project','symbol'].includes(k))||Object.values(w).some(v=>!Number.isFinite(v)||v<0||v>100)||!Object.values(w).some(v=>v>0))throw Error('weight invalid');
 const q=grams(query),qp=[...model.graph.keys()].filter(p=>includes(query,p)),qs=model.legend.filter(([s,t])=>query.includes(s)||includes(query,t)).map(([s])=>s);
 return model.nodes.map(node=>{const character=cosine(q,node.grams),project=node.projects.some(p=>qp.includes(p))?1:node.projects.some(p=>qp.some(q=>model.graph.get(q).has(p)))?0.5:0,symbol=node.symbols.some(s=>qs.includes(s))?1:0;return {node,score:w.character*character+w.project*project+w.symbol*symbol};}).sort((a,b)=>b.score-a.score||a.node.origins[0]-b.node.origins[0]);
}
export function recombine(model,query,{seed=1,steps=3,words=4,weights={},association=0.8}={}){
 if(!Number.isInteger(seed)||seed<0||seed>0xffffffff||!Number.isInteger(steps)||steps<1||steps>16||!Number.isInteger(words)||words<1||words>32||!Number.isFinite(association)||association<0||association>1)throw Error('generation limit');
 let state=seed>>>0;const random=()=>{state=(Math.imul(1664525,state)+1013904223)>>>0;return state/4294967296;};
 const used=new Set(),fragments=[];let current=query;
 for(let i=0;i<steps;i++){const pool=rank(model,current,{weights}).filter(r=>!used.has(r.node.id)).slice(0,32);if(!pool.length)break;const masses=pool.map(r=>association*r.score+(1-association)*0.1+1e-9);let pick=random()*masses.reduce((a,b)=>a+b,0),j=0;while(j<pool.length-1&&pick>=masses[j])pick-=masses[j++];const {node,score}=pool[j];used.add(node.id);const tokens=[...node.text.matchAll(/\S+/gu)];const start=Math.floor(random()*tokens.length),end=Math.min(tokens.length-1,start+words-1);const from=tokens[start].index,to=tokens[end].index+tokens[end][0].length;const text=node.text.slice(from,to);fragments.push({id:node.id,origins:[...node.origins],from,to,text,score});current=(query+' '+text+' '+node.projects.join(' ')).slice(0,8192);}
 return {kind:'synthetic_association',verifiedFact:false,seed,fragments,text:fragments.map(f=>f.text).join(' | ')};
}
