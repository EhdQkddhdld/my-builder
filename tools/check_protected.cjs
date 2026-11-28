#!/usr/bin/env node
'use strict';
// Byte-exact source guard for the 15 approved core declarations.
// Node 22.16.0 provides the bundled Acorn parser; no application dependency.
const fs = require('node:fs');
const acorn = require('internal/deps/acorn/acorn/dist/acorn');
const names = [
  'assignTough', 'scanFlatGroups', 'validateShotRegistry', 'rd210ValidSlots',
  'canAssignTough', 'applyFramingCascade', 'generate', 'POSE_SHOT_CONFIG',
  'SHOT_TEMPLATES', 'EXTRA_SHOT_DEFS', 'CONFLICT_GROUPS', 'POSE_BY_COUNT',
  'CORE_BED_1V1_IDS', 'ARCHIVED_POSE_IDS', 'TOUGH_ACTION_LIB'
];
const wanted = new Set(names);
const jsTypes = new Set(['','text/javascript','application/javascript','module','text/ecmascript','application/ecmascript']);
function collect(path) {
  const html = fs.readFileSync(path,'utf8');
  const found = new Map(names.map(n => [n,[]]));
  const scripts = /<script\b([^>]*)>([\s\S]*?)<\/script\s*>/gi;
  let match;
  let count = 0;
  while ((match = scripts.exec(html)) !== null) {
    const attrs = match[1];
    if (/\bsrc\s*=/i.test(attrs)) continue;
    const type = (/\btype\s*=\s*["']([^"']+)["']/i.exec(attrs)?.[1] || '').trim().toLowerCase();
    if (!jsTypes.has(type)) continue;
    const source = match[2];
    if (!source.trim()) continue;
    count++;
    const ast = acorn.parse(source,{ecmaVersion:'latest',sourceType:type==='module'?'module':'script',allowHashBang:true});
    function visit(node) {
      if (!node || typeof node !== 'object') return;
      if (node.type==='FunctionDeclaration' && node.id && wanted.has(node.id.name)) {
        // The protected generate is the original synchronous engine,
        // not the separate async API function of the same name.
        if (node.id.name!=='generate' || !node.async) {
          found.get(node.id.name).push(source.slice(node.start,node.end));
        }
      }
      if (node.type==='VariableDeclaration') {
        for (const decl of node.declarations) {
          if (decl.id.type==='Identifier' && wanted.has(decl.id.name)) {
            found.get(decl.id.name).push(source.slice(node.start,node.end));
          }
        }
      }
      for (const value of Object.values(node)) {
        if (Array.isArray(value)) for (const item of value) visit(item);
        else if (value && typeof value==='object') visit(value);
      }
    }
    visit(ast);
  }
  if (!count) throw new Error('No executable inline scripts: '+path);
  for (const [name, blocks] of found) {
    if (blocks.length!==1) throw new Error(path+': '+name+' matched '+blocks.length+' declarations; expected exactly 1');
  }
  return found;
}
try {
  if (process.argv.length!==4) throw new Error('Usage: node --expose-internals tools/check_protected.cjs BASE_HTML CANDIDATE_HTML');
  const base=collect(process.argv[2]), candidate=collect(process.argv[3]);
  let pass=0;
  for (const name of names) {
    const equal=base.get(name)[0]===candidate.get(name)[0];
    console.log((equal?'PASS ':'CHANGED ')+name);
    if (equal) pass++;
  }
  console.log('Protected blocks unchanged: '+pass+'/'+names.length);
  if (pass!==names.length) process.exitCode=1;
} catch (err) {
  console.error('Protected block check failed:',err.message);
  process.exitCode=1;
}
