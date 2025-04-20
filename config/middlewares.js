
module.exports = [
  'strapi::errors',
  {
    name: 'strapi::cors',
    config: {
      origin: ['https://rolleilookup.com'],
      headers: ['Content-Type', 'Authorization', 'X-Frame-Options'],
    },
  },
  'strapi::security',
  'strapi::poweredBy',
  'strapi::logger',
  'strapi::query',
  'strapi::body',
  'strapi::session',
  'strapi::favicon',
  'strapi::public',
];
