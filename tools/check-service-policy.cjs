const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.resolve(__dirname, '..');
const read = (file) => fs.readFileSync(path.join(root, file), 'utf8');
let schemaCount = 0;
for (const file of fs.readdirSync(root).filter((name) => name.endsWith('.html'))) {
  const html = read(file);
  assert(!/part.time|employee|staff|workers|arrangementers|info@betterbeds.pro/i.test(html), file);
  assert(!/<(?:option|input)[^>]*\binstall/i.test(html), file + ': installation intake option');
  assert(!/We Install It|Scheduled installs available|Professional installation|same.day install|minPrice": 3000/i.test(html), file + ': obsolete service promise');
  for (const match of html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)) {
    JSON.parse(match[1]);
    schemaCount += 1;
  }
}
const knowledge = JSON.parse(read('data/faq-knowledge.json'));
assert(!/part.time|workers|staff|employee|arrangementers/i.test(JSON.stringify(knowledge)));
for (const entry of knowledge.entries) {
  assert(!/\$3,000|installation starts|installs are by appointment|Yes\. Better Beds installs/i.test(entry.answer), entry.id);
}
const profile = JSON.parse(read('.well-known/agent.json'));
assert(!profile.services.some((service) => /install/i.test(service.name)));
assert(profile.safe_answer_rules.some((rule) => rule.includes('Never offer, schedule, or quote installation')));

// Exercise the widget's actual policy functions without building a DOM or making requests.
const source = read('faq-widget.js').replace(
  '  const addMessage =',
  '  globalThis.policyTest = { servicePolicyAnswer, enforceServicePolicy };\n  const addMessage ='
);
const sandbox = { document: { readyState: 'loading', addEventListener() {} } };
vm.runInNewContext(source, sandbox);
const { servicePolicyAnswer, enforceServicePolicy } = sandbox.policyTest;
for (const question of [
  'Do you install beds?',
  'Can you install my 2019 Silverado bed on Saturday?',
  'How much does installation cost?',
  'Is installation included?',
  'Can you remove my existing truck bed?',
  'Will you swap my bed?'
]) {
  assert(servicePolicyAnswer(question).includes('no longer offers installation'), question);
}
for (const question of ['Can you load it onto my trailer?', 'Do you have a forklift?']) {
  assert(servicePolicyAnswer(question).includes('forklift'), question);
}
for (const reply of [
  'Yes, we install beds by appointment.',
  'Installation starts at $250.',
  'We can remove your old bed and bolt on the new one.',
  'We install lift kits too.'
]) {
  assert(enforceServicePolicy(reply).includes('no longer offers installation'), reply);
}
assert.equal(servicePolicyAnswer('Do you have a Silverado bed in stock?'), '');
assert.equal(enforceServicePolicy('Text photos for inventory confirmation.'), 'Text photos for inventory confirmation.');
console.log('PASS: ' + schemaCount + ' structured-data blocks; intake, saved FAQ, agent profile, and chatbot service policy.');
