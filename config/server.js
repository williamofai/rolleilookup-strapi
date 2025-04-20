
module.exports = ({ env }) => ({
  host: env('HOST', '0.0.0.0'),
  port: env.int('PORT', 1337),
  url: env('URL', 'http://localhost:1337'),
  admin: {
    url: env('ADMIN_URL', '/admin'),
  },
  app: {
    keys: env.array('APP_KEYS'),
  },
  proxy: true, // Trust proxy headers from Nginx
});
