'use strict';

const { crearApp } = require('./app');

const puerto = process.env.PORT || 3000;
crearApp().listen(puerto, () => console.log(`ia-service escuchando en el puerto ${puerto}`));
