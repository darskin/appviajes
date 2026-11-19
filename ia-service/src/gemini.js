'use strict';

const MODELO = process.env.GEMINI_MODEL || 'gemini-flash-latest';

function construirPrompt({ destino, presupuesto, dias }) {
  return [
    'Eres un asistente de viajes. Responde siempre en español.',
    `Crea un itinerario de ${dias} día(s) para el destino "${destino}" en Colombia o alrededores,`,
    `con un presupuesto total de ${presupuesto} pesos colombianos (COP).`,
    'Para cada día da: actividades de mañana, tarde y noche, y un costo aproximado en COP.',
    'Al final indica si el plan cabe en el presupuesto. Usa texto simple, sin tablas.',
  ].join(' ');
}

const MODELOS_RESPALDO = (process.env.GEMINI_FALLBACK_MODELS || 'gemini-flash-lite-latest')
  .split(',').map((m) => m.trim()).filter(Boolean);
const REINTENTABLES = new Set([429, 500, 502, 503, 504]);

function errorHttp(status, estado) {
  const err = new Error(estado);
  err.status = status;
  return err;
}

/** Una llamada a un modelo. Devuelve { texto } o { estado, detalle } si el proveedor respondió con error. */
async function llamarModelo(modelo, datos, apiKey, fetchFn) {
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${modelo}:generateContent`;
  let respuesta;
  try {
    respuesta = await fetchFn(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'x-goog-api-key': apiKey },
      body: JSON.stringify({ contents: [{ parts: [{ text: construirPrompt(datos) }] }] }),
      signal: AbortSignal.timeout(20000),
    });
  } catch (e) {
    return { estado: 0, detalle: 'sin respuesta' };
  }
  if (!respuesta.ok) {
    let detalle = '';
    try {
      detalle = (await respuesta.json())?.error?.message || '';
    } catch (e) { /* sin detalle */ }
    return { estado: respuesta.status, detalle };
  }
  const json = await respuesta.json();
  const texto = json?.candidates?.[0]?.content?.parts?.map((p) => p.text).join('').trim();
  return texto ? { texto } : { estado: 200, detalle: 'respuesta vacía' };
}

/**
 * Llama a la API REST de Gemini y devuelve el texto generado.
 * Si el proveedor está saturado (429/5xx) reintenta una vez y luego prueba los modelos de respaldo.
 */
async function generarItinerario(
  datos,
  { fetchFn = fetch, apiKey = process.env.GEMINI_API_KEY, esperar = (ms) => new Promise((r) => setTimeout(r, ms)) } = {},
) {
  if (!apiKey) throw errorHttp(503, 'El servicio de IA no está configurado (falta GEMINI_API_KEY).');

  let ultimo = { estado: 0, detalle: '' };
  let modeloUltimo = MODELO;
  for (const modelo of [MODELO, ...MODELOS_RESPALDO.filter((m) => m !== MODELO)]) {
    for (let intento = 0; intento < 2; intento += 1) {
      const r = await llamarModelo(modelo, datos, apiKey, fetchFn);
      if (r.texto) return r.texto;
      ultimo = r;
      modeloUltimo = modelo;
      if (r.estado !== 0 && !REINTENTABLES.has(r.estado)) break; // error definitivo de este modelo
      if (intento === 0) await esperar(1500);
    }
  }
  const razon = ultimo.estado === 0 ? 'No se pudo contactar al proveedor de IA' : `El proveedor de IA respondió con error ${ultimo.estado}`;
  throw errorHttp(502, `${razon} (modelo ${modeloUltimo})${ultimo.detalle ? `: ${ultimo.detalle.slice(0, 200)}` : '.'}`);
}

module.exports = { generarItinerario, construirPrompt };
