const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { betterBedsFaqAnswer } = require('../faq-widget.js');

const root = path.resolve(__dirname, '..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');
let schemaCount = 0;
for (const file of fs.readdirSync(root).filter(name => name.endsWith('.html'))) {
  const html = read(file);
  assert(!/<(?:option|input)[^>]*\binstall/i.test(html), file + ': installation intake option');
  assert(!/We Install It|Scheduled installs available|Professional installation|same.day install|We Find It|We Repair It/i.test(html), file + ': obsolete service promise');
  for (const match of html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)) {
    JSON.parse(match[1]);
    schemaCount++;
  }
}
const knowledge = JSON.parse(read('data/faq-knowledge.json'));
const profile = JSON.parse(read('.well-known/agent.json'));
assert(!profile.services.some(service => /install/i.test(service.name)));
assert(profile.safe_answer_rules.some(rule => /never offer installation or removal/i.test(rule)));
assert(!read('faq-widget.js').includes('chat.betterbeds.pro'), 'Do not query the legacy repair-oriented chatbot');

// Exercise the same answer resolver used by the website, including questions
// that could otherwise imply services or unconfirmed inventory.
for (const question of [
  'Do you install beds?',
  'Can you install my 2019 Silverado bed on Saturday?',
  'How much does installation cost?',
  'Is installation included?',
  'Can you remove my existing truck bed?',
  'Will you swap my bed?'
]) {
  assert(betterBedsFaqAnswer(question, knowledge.entries).includes('Installation and removal are not offered'), question);
}
for (const question of ['Can you load it onto my trailer?', 'Do you have a forklift?']) {
  assert(betterBedsFaqAnswer(question, knowledge.entries).includes('Forklift loading'), question);
}
const inventoryAnswer = betterBedsFaqAnswer('Do you have a Silverado bed in stock?', knowledge.entries);
assert(inventoryAnswer.includes('confirm availability'), 'Stock must be confirmed');
assert(!/yes.*silverado/i.test(inventoryAnswer), 'Do not invent unlisted stock');
const olderAnswer = betterBedsFaqAnswer('Do you repair and paint older beds?', knowledge.entries);
assert(olderAnswer.includes('older beds') && olderAnswer.includes('by arrangement'));
assert(betterBedsFaqAnswer('Can you find me a bed?', knowledge.entries).includes('not advertising a bed-finding service'));
assert(betterBedsFaqAnswer('Unrecognized question', []).includes('Call or text 214-524-8401'));
assert(betterBedsFaqAnswer('', knowledge.entries, 'photos').includes('not photographs'));
for (const question of ['What does available to order mean?', 'Can I pick up an available-to-order bed today?', 'What is the expected arrival for a preorder Ford bed?']) {
  assert(betterBedsFaqAnswer(question, knowledge.entries).includes('not at our Dallas shop'), question);
}
console.log(`PASS: ${schemaCount} structured-data blocks; sales focus, no installation promises, confirmed-stock answers, older inventory scope, and FAQ fallback.`);
