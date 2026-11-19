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

/** Llama a la API REST de Gemini y devuelve el texto generado. */
async function generarItinerario(datos, { fetchFn = fetch, apiKey = process.env.GEMINI_API_KEY } = {}) {
  if (!apiKey) {
    const err = new Error('El servicio de IA no está configurado (falta GEMINI_API_KEY).');
    err.status = 503;
    throw err;
  }
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${MODELO}:generateContent`;
  let respuesta;
  try {
    respuesta = await fetchFn(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'x-goog-api-key': apiKey },
      body: JSON.stringify({ contents: [{ parts: [{ text: construirPrompt(datos) }] }] }),
      signal: AbortSignal.timeout(45000),
    });
  } catch (e) {
    const err = new Error('No se pudo contactar al proveedor de IA.');
    err.status = 502;
    throw err;
  }
  if (!respuesta.ok) {
    let detalle = '';
    try {
      detalle = (await respuesta.json())?.error?.message || '';
    } catch (e) { /* sin detalle */ }
    const err = new Error(
      `El proveedor de IA respondió con error ${respuesta.status} (modelo ${MODELO})` +
      (detalle ? `: ${detalle.slice(0, 200)}` : '.')
    );
    err.status = 502;
    throw err;
  }
  const json = await respuesta.json();
  const texto = json?.candidates?.[0]?.content?.parts?.map((p) => p.text).join('').trim();
  if (!texto) {
    const err = new Error('El proveedor de IA no devolvió contenido.');
    err.status = 502;
    throw err;
  }
  return texto;
}

module.exports = { generarItinerario, construirPrompt };
