
module.exports = [
  'strapi::errors',
  {
    name: 'strapi::cors',
    config: {
      origin: ['https://rolleilookup.com', 'https://rolleilookup.com/admin'],
      headers: ['Content-Type', 'Authorization', 'X-Frame-Options', 'Origin', 'Accept'],
      methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    },
  },
  {
    name: 'strapi::security',
    config: {
      contentSecurityPolicy: {
        useDefaults: true,
        directives: {
          'connect-src': ["'self'", 'https:', 'http:'],
          'img-src': ["'self'", 'data:', 'blob:', 'https://*.digitaloceanspaces.com'],
          'media-src': ["'self'", 'data:', 'blob:', 'https://*.digitaloceanspaces.com'],
          'script-src': ["'self'", "'unsafe-inline'", 'https://rolleilookup.com'],
          'style-src': ["'self'", "'unsafe-inline'"],
          upgradeInsecureRequests: null,
        },
      },
    },
  },
  'strapi::poweredBy',
  'strapi::logger',
  'strapi::query',
  'strapi::body',
  'strapi::session',
  'strapi::favicon',
  'strapi::public',
  'global::error-handler',
];
