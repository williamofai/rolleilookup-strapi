module.exports = ({ env }) => ({
  // Configure the users-permissions plugin
  'users-permissions': {
    config: {
      jwtSecret: env('JWT_SECRET'),
    },
  },
});
