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
const wanted = new Set([...names, 'POSE_AFTER_BY_COUNT']);
const approvedInsertTypes = new Map([
  ['tentacle-suspend', 'vaginal'], ['tentacle-wrap', null], ['tentacle-dp', 'dp'],
  ['tentacle-wall', 'vaginal'], ['tentacle-pit', 'vaginal']
]);
const approvalIds = [...approvedInsertTypes.keys()];
const registryNames = ['POSE_BY_COUNT', 'POSE_SHOT_CONFIG'];
const jsTypes = new Set(['','text/javascript','application/javascript','module','text/ecmascript','application/ecmascript']);
function collect(path) {
  const html = fs.readFileSync(path,'utf8');
  const found = new Map([...wanted].map(n => [n,[]]));
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

function propertyName(property) {
  if (property.type !== 'Property' || property.computed || property.method ||
      property.shorthand || property.kind !== 'init') return undefined;
  return property.key.type === 'Identifier' ? property.key.name :
    typeof property.key.value === 'string' ? property.key.value : undefined;
}

function properties(object) {
  if (object?.type !== 'ObjectExpression') throw new Error('Expected a literal registry object');
  const result = new Map();
  for (const property of object.properties) {
    const key = propertyName(property);
    if (key === undefined || key === '__proto__' || result.has(key)) {
      throw new Error('Invalid or duplicate registry key: '+key);
    }
    result.set(key, property);
  }
  return result;
}

function literalData(node) {
  if (node.type === 'Literal') return node.value === null ||
    ['string', 'number', 'boolean'].includes(typeof node.value);
  if (node.type === 'ArrayExpression') return node.elements.every(item => item && literalData(item));
  if (node.type === 'ObjectExpression') return [...properties(node).values()].every(p => literalData(p.value));
  return false;
}

function readRegistry(source, name) {
  const [statement, ...rest] = acorn.parse(source, {ecmaVersion:'latest'}).body;
  const declaration = statement?.declarations?.[0];
  if (rest.length || statement.kind !== 'const' || statement.declarations.length !== 1 ||
      declaration.id.name !== name) throw new Error('Unexpected registry declaration: '+name);
  return properties(declaration.init);
}

function approvedAddition(name, base, candidate, addedKeys, validAddition) {
  const before = base.get(name)[0], after = candidate.get(name)[0];
  const oldEntries = readRegistry(before, name), newEntries = readRegistry(after, name);
  const retained = [...newEntries.keys()].filter(key => oldEntries.has(key));
  const additions = [...newEntries.keys()].filter(key => !oldEntries.has(key));
  if (retained.length !== oldEntries.size || additions.length !== addedKeys.length ||
      !addedKeys.every(key => additions.includes(key))) return false;
  const sourceOf = (source, property) => source.slice(property.start, property.end);
  return [...oldEntries].every(([key, property], index) =>
    retained[index] === key && sourceOf(before, property) === sourceOf(after, newEntries.get(key))) &&
    additions.every(key => {
      const node = newEntries.get(key).value;
      return literalData(node) && validAddition(node, key);
    });
}

function validPoseGroup(node) {
  if (node.type !== 'ArrayExpression' || node.elements.length !== approvalIds.length) return false;
  const ids = node.elements.map(pose => pose.type === 'ObjectExpression' ?
    properties(pose).get('id')?.value.value : undefined);
  return approvalIds.every(id => ids.includes(id));
}

function validShotConfig(node, id, templates) {
  if (node.type !== 'ObjectExpression') return false;
  const fields = properties(node);
  return fields.size === 3 && fields.get('maxHands')?.value.value === 0 &&
    fields.get('insertType')?.value.value === approvedInsertTypes.get(id) &&
    templates.has(fields.get('tpl')?.value.value);
}

function approvedRegistryCounts(before, after) {
  const activeCount = '=== [73,22][index]';
  const totalCount = 'poses.size === 95 && Object.keys(POSE_SHOT_CONFIG).length === 95';
  if (before.split(activeCount).length !== 2 || before.split(totalCount).length !== 2) return false;
  return after === before.replace(activeCount, '=== [78,22][index]')
    .replace(totalCount, 'poses.size === 100 && Object.keys(POSE_SHOT_CONFIG).length === 100');
}

function approvedTentacleGenerator(before, after) {
  const soloBranch = `  if(count==='solo' || !count){
    const head=count==="solo"?"1girl, solo":selectedChar?"1girl":"";`;
  const extendedBranch = `  if(count==='solo' || count==="tentacles" || !count){
    const head=count==="solo"?"1girl, solo":count==="tentacles"||selectedChar?"1girl":"";
    const tentacleTags=count==="tentacles" ? [activePose?mainDescOut:"tentacles", tentaclePulloutTags(isPulledOut,insertType,shot)] : [];`;
  const poseTags = 'effectiveSkinTags,addonRes.tagsText,clothStateStr,girlPoseOut,pulledOutGirl,femaleHandTag';
  if (before.split(soloBranch).length !== 2 || before.split(poseTags).length !== 2) return false;
  return after === before.replace(soloBranch, extendedBranch)
    .replace(poseTags, poseTags.replace('girlPoseOut', '...tentacleTags,girlPoseOut'));
}

try {
  if (process.argv.length!==4) throw new Error('Usage: node --expose-internals tools/check_protected.cjs BASE_HTML CANDIDATE_HTML');
  const base=collect(process.argv[2]), candidate=collect(process.argv[3]);
  if (base.get('POSE_AFTER_BY_COUNT')[0] !== candidate.get('POSE_AFTER_BY_COUNT')[0]) {
    throw new Error('Legacy pose registry changed: POSE_AFTER_BY_COUNT');
  }
  const registryChanges = registryNames.filter(name => base.get(name)[0] !== candidate.get(name)[0]);
  const templates = registryChanges.length ? readRegistry(base.get('SHOT_TEMPLATES')[0], 'SHOT_TEMPLATES') : null;
  const approved = registryChanges.length === registryNames.length &&
    approvedRegistryCounts(base.get('validateShotRegistry')[0], candidate.get('validateShotRegistry')[0]) &&
    approvedTentacleGenerator(base.get('generate')[0], candidate.get('generate')[0]) &&
    approvedAddition('POSE_BY_COUNT', base, candidate, ['tentacles'], validPoseGroup) &&
    approvedAddition('POSE_SHOT_CONFIG', base, candidate, approvalIds,
      (node, id) => validShotConfig(node, id, templates));
  let pass=0;
  for (const name of names) {
    const equal=base.get(name)[0]===candidate.get(name)[0];
    const allowed = approved && (registryNames.includes(name) || ['validateShotRegistry','generate'].includes(name));
    console.log((equal?'PASS ':allowed?'APPROVED CHANGE ':'CHANGED ')+name);
    if (equal || allowed) pass++;
  }
  console.log('Protected blocks passed: '+pass+'/'+names.length);
  if (pass === names.length) console.log(approved?'DEEP_TRACK':'PROTECTED_CHANGED=0');
  if (pass!==names.length) process.exitCode=1;
} catch (err) {
  console.error('Protected block check failed:',err.message);
  process.exitCode=1;
}
