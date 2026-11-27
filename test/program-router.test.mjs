import test from 'node:test';
import assert from 'node:assert/strict';
import {routeProgram,programCatalog} from '../program-router.mjs';

test('public deterministic program uses browser lane, not CI or model',()=>{
 const r=routeProgram('resonance.calculate');
 assert.equal(r.lane,'browser');
 assert.equal(r.repository,'www-infinity4/QuantaPhi');
 assert.equal(r.status,'route_only');
 assert.equal(r.executionAuthorized,false);
});
test('private chat remains blocked pending verified independent inference host',()=>{
 const r=routeProgram('conversation.reply');
 assert.equal(r.lane,'private-api');
 assert.equal(r.status,'host_unverified');
 assert.equal(r.executionAuthorized,false);
});
test('engineering and maintenance use existing signed runner, never a public dispatch',()=>{
 for(const id of ['repository.engineer','repository.monitor']){
  const r=routeProgram(id);
  assert.equal(r.lane,'signed-repository');
  assert.equal(r.executionAuthorized,false);
  assert.equal(r.status,'authorization_required');
 }
});
test('arbitrary paths, commands and spoofed authorization are refused',()=>{
 for(const id of ['__proto__','constructor','https://example.org','../../x','git push','',null,{},['resonance.calculate']]){
  assert.deepEqual(routeProgram(id),{status:'unknown_program',executionAuthorized:false});
 }
 assert.equal(routeProgram('repository.engineer',{owner:true,authorized:true}).executionAuthorized,false);
});
test('catalog cannot be mutated and route receipts carry no input or private data',()=>{
 assert.ok(Object.isFrozen(programCatalog));
 for(const entry of programCatalog)assert.ok(Object.isFrozen(entry));
 const r=routeProgram('conversation.reply',{prompt:'private canary'});
 assert.doesNotMatch(JSON.stringify(r),/private canary/);
 assert.equal(r.completed,false);
});
