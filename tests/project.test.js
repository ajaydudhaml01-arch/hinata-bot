const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');

test('package metadata is suitable for an open-source project', () => {
  const pkg = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8'));

  assert.equal(pkg.name, 'hinata-discord-bot');
  assert.equal(pkg.license, 'MIT');
  assert.equal(pkg.main, 'index.js');
  assert.equal(pkg.scripts.start, 'node index.js');
  assert.ok(pkg.repository);
  assert.ok(Array.isArray(pkg.keywords));
  assert.ok(pkg.keywords.includes('discord-bot'));
});

test('example configuration has the expected shape', () => {
  const config = JSON.parse(
    fs.readFileSync(path.join(root, 'config.example.json'), 'utf8')
  );

  assert.ok(config.colors);
  assert.ok(config.defaultSettings);
  assert.equal(typeof config.defaultSettings.welcomeRoleName, 'string');
  assert.ok(Array.isArray(config.defaultSettings.blockedWords));
  assert.equal(typeof config.defaultSettings.levelRoles, 'object');
});

test('secret environment file is ignored while example is tracked', () => {
  const ignore = fs.readFileSync(path.join(root, '.gitignore'), 'utf8');

  assert.match(ignore, /^\.env$/m);
  assert.match(ignore, /^!\.env\.example$/m);
});
