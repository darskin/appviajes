'use strict';

const test = require('node:test');
const assert = require('node:assert');
const { crearApp } = require('../src/app');
const { generarItinerario } = require('../src/gemini');

async function conServidor(opciones, fn) {
  const servidor = crearApp(opciones).listen(0);
  const base = `http://127.0.0.1:${servidor.address().port}`;
  try { await fn(base); } finally { servidor.close(); }
}

const post = (base, cuerpo, headers = {}) =>
  fetch(`${base}/api/itinerario`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...headers },
    body: JSON.stringify(cuerpo),
  });

const valido = { destino: 'Guatavita', presupuesto: 300000, dias: 2 };

test('GET /health responde ok', () =>
  conServidor({}, async (b) => {
    const r = await fetch(`${b}/health`);
    assert.strictEqual(r.status, 200);
    assert.deepStrictEqual(await r.json(), { estado: 'ok' });
  }));

test('Swagger: /docs y /openapi.json son públicos', () =>
  conServidor({ serviceApiKey: 'secreta' }, async (b) => {
    assert.strictEqual((await fetch(`${b}/docs/`)).status, 200);
    const spec = await (await fetch(`${b}/openapi.json`)).json();
    assert.ok(spec.paths['/api/itinerario']);
  }));

test('POST válido devuelve el itinerario del generador', () =>
  conServidor({ generar: async () => 'Día 1: laguna' }, async (b) => {
    const r = await post(b, valido);
    assert.strictEqual(r.status, 200);
    assert.strictEqual((await r.json()).itinerario, 'Día 1: laguna');
  }));

test('POST con datos inválidos responde 400', () =>
  conServidor({ generar: async () => 'x' }, async (b) => {
    for (const mal of [{}, { ...valido, presupuesto: 0 }, { ...valido, dias: 0 }, { ...valido, dias: 15 },
                       { ...valido, destino: '  ' }, { ...valido, presupuesto: '100' }]) {
      assert.strictEqual((await post(b, mal)).status, 400);
    }
  }));

test('Con SERVICE_API_KEY exige X-API-Key', () =>
  conServidor({ serviceApiKey: 'secreta', generar: async () => 'ok' }, async (b) => {
    assert.strictEqual((await post(b, valido)).status, 401);
    assert.strictEqual((await post(b, valido, { 'X-API-Key': 'mala' })).status, 401);
    assert.strictEqual((await post(b, valido, { 'X-API-Key': 'secreta' })).status, 200);
  }));

test('Un fallo de la IA se informa con su código', () =>
  conServidor({ generar: async () => { const e = new Error('IA caída'); e.status = 502; throw e; } }, async (b) => {
    const r = await post(b, valido);
    assert.strictEqual(r.status, 502);
    assert.strictEqual((await r.json()).error, 'IA caída');
  }));

test('gemini: sin clave responde 503', async () => {
  await assert.rejects(generarItinerario(valido, { apiKey: '' }), (e) => e.status === 503);
});

test('gemini: extrae el texto de la respuesta del proveedor', async () => {
  const fetchFn = async (url, opts) => {
    assert.match(url, /generateContent$/);
    assert.strictEqual(opts.headers['x-goog-api-key'], 'k');
    return { ok: true, json: async () => ({ candidates: [{ content: { parts: [{ text: 'Plan ' }, { text: 'listo' }] } }] }) };
  };
  assert.strictEqual(await generarItinerario(valido, { fetchFn, apiKey: 'k' }), 'Plan listo');
});

test('gemini: error del proveedor o respuesta vacía responde 502', async () => {
  await assert.rejects(generarItinerario(valido, { fetchFn: async () => ({ ok: false, status: 429 }), apiKey: 'k' }), (e) => e.status === 502);
  await assert.rejects(generarItinerario(valido, { fetchFn: async () => ({ ok: true, json: async () => ({}) }), apiKey: 'k' }), (e) => e.status === 502);
});
