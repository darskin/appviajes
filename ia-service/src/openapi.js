'use strict';

module.exports = {
  openapi: '3.0.3',
  info: {
    title: 'AppViajes - ia-service',
    version: '1.0.0',
    description:
      'Microservicio Node.js que genera itinerarios de viaje con IA generativa (Gemini). ' +
      'Lo consume la aplicación Django. El itinerario no se guarda.',
  },
  tags: [
    { name: 'Itinerarios', description: 'Generación de itinerarios con IA' },
    { name: 'Salud', description: 'Estado del servicio' },
  ],
  paths: {
    '/health': {
      get: {
        tags: ['Salud'],
        summary: 'Comprueba que el servicio está activo',
        responses: {
          200: {
            description: 'Servicio activo',
            content: { 'application/json': { schema: { type: 'object', properties: { estado: { type: 'string', example: 'ok' } } } } },
          },
        },
      },
    },
    '/api/itinerario': {
      post: {
        tags: ['Itinerarios'],
        summary: 'Genera un itinerario según destino, presupuesto y días',
        description: 'Si el servicio tiene SERVICE_API_KEY configurada, se debe enviar en el encabezado X-API-Key.',
        security: [{ ApiKeyAuth: [] }],
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: { $ref: '#/components/schemas/SolicitudItinerario' },
              example: { destino: 'Guatavita', presupuesto: 300000, dias: 2 },
            },
          },
        },
        responses: {
          200: {
            description: 'Itinerario generado',
            content: { 'application/json': { schema: { $ref: '#/components/schemas/RespuestaItinerario' } } },
          },
          400: { description: 'Datos inválidos', content: { 'application/json': { schema: { $ref: '#/components/schemas/Error' } } } },
          401: { description: 'Falta o es incorrecta la clave X-API-Key', content: { 'application/json': { schema: { $ref: '#/components/schemas/Error' } } } },
          502: { description: 'Falló el proveedor de IA', content: { 'application/json': { schema: { $ref: '#/components/schemas/Error' } } } },
          503: { description: 'Servicio de IA no configurado', content: { 'application/json': { schema: { $ref: '#/components/schemas/Error' } } } },
        },
      },
    },
  },
  components: {
    securitySchemes: { ApiKeyAuth: { type: 'apiKey', in: 'header', name: 'X-API-Key' } },
    schemas: {
      SolicitudItinerario: {
        type: 'object',
        required: ['destino', 'presupuesto', 'dias'],
        properties: {
          destino: { type: 'string', maxLength: 200, example: 'Guatavita' },
          presupuesto: { type: 'integer', minimum: 1, description: 'Presupuesto total en COP', example: 300000 },
          dias: { type: 'integer', minimum: 1, maximum: 14, example: 2 },
        },
      },
      RespuestaItinerario: {
        type: 'object',
        properties: {
          destino: { type: 'string' },
          presupuesto: { type: 'integer' },
          dias: { type: 'integer' },
          itinerario: { type: 'string', description: 'Texto del itinerario generado por la IA' },
        },
      },
      Error: { type: 'object', properties: { error: { type: 'string' } } },
    },
  },
};
