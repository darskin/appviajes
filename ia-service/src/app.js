'use strict';

const crypto = require('node:crypto');
const express = require('express');
const swaggerUi = require('swagger-ui-express');
const openapi = require('./openapi');
const { generarItinerario } = require('./gemini');

function clavesIguales(a, b) {
  const x = Buffer.from(String(a));
  const y = Buffer.from(String(b));
  return x.length === y.length && crypto.timingSafeEqual(x, y);
}

function validar({ destino, presupuesto, dias } = {}) {
  if (typeof destino !== 'string' || !destino.trim() || destino.length > 200) {
    return 'El destino es obligatorio (máximo 200 caracteres).';
  }
  if (!Number.isInteger(presupuesto) || presupuesto < 1) {
    return 'El presupuesto debe ser un entero mayor que cero.';
  }
  if (!Number.isInteger(dias) || dias < 1 || dias > 14) {
    return 'Los días deben ser un entero entre 1 y 14.';
  }
  return null;
}

function crearApp({ generar = generarItinerario, serviceApiKey = process.env.SERVICE_API_KEY } = {}) {
  const app = express();
  app.use(express.json({ limit: '10kb' }));

  app.get('/', (req, res) => res.redirect('/docs'));
  app.get('/health', (req, res) => res.json({ estado: 'ok' }));
  app.get('/openapi.json', (req, res) => res.json(openapi));
  app.use('/docs', swaggerUi.serve, swaggerUi.setup(openapi));

  app.post('/api/itinerario', async (req, res) => {
    if (serviceApiKey && !clavesIguales(req.get('X-API-Key') || '', serviceApiKey)) {
      return res.status(401).json({ error: 'Clave de API inválida.' });
    }
    const problema = validar(req.body);
    if (problema) return res.status(400).json({ error: problema });

    const { destino, presupuesto, dias } = req.body;
    try {
      const itinerario = await generar({ destino: destino.trim(), presupuesto, dias });
      return res.json({ destino: destino.trim(), presupuesto, dias, itinerario });
    } catch (e) {
      return res.status(e.status || 502).json({ error: e.message });
    }
  });

  return app;
}

module.exports = { crearApp };
