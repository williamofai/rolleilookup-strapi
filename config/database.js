module.exports = ({ env }) => ({
  connection: {
    client: 'postgres',
    connection: {
      host: env('DATABASE_HOST', 'localhost'),
      port: env.int('DATABASE_PORT', 5432),
      database: env('DATABASE_NAME', 'rolleiflex_strapi_db'),
      user: env('DATABASE_USERNAME', 'rolleiflex'),
      password: env('DATABASE_PASSWORD', 'idcc8Wv3kpHjnNLpaoKKyhLYaYEWJr49'),
      ssl: env.bool('DATABASE_SSL', false),
      schema: env('DATABASE_SCHEMA', 'public'),
    },
    pool: { min: env.int('DATABASE_POOL_MIN', 2), max: env.int('DATABASE_POOL_MAX', 10) },
    acquireConnectionTimeout: env.int('DATABASE_CONNECTION_TIMEOUT', 60000),
  },
});
