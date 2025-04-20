'use strict';

const { Client } = require('pg');

module.exports = {
  async find(ctx) {
    // Set up PostgreSQL client for rolleiflex_db
    const client = new Client({
      host: '127.0.0.1',
      port: 5432,
      database: 'rolleiflex_db',
      user: 'rolleiflex',
      password: 'idcc8Wv3kpHjnNLpaoKKyhLYaYEWJr49',
    });

    try {
      // Connect to the database
      await client.connect();

      // Query the rolleiflex_cameras table
      const result = await client.query('SELECT * FROM rolleiflex_cameras');

      // Transform the data to match Strapi's API response format
      const formattedData = result.rows.map(row => ({
        id: row.id,
        attributes: {
          serial_start: row.serial_start,
          serial_end: row.serial_end,
          model_name: row.model_name,
          year_produced: row.year_produced,
          taking_lens: row.taking_lens,
          looking_lens: row.looking_lens,
          description: row.description,
        },
      }));

      return {
        data: formattedData,
        meta: {
          pagination: {
            page: 1,
            pageSize: result.rows.length,
            pageCount: 1,
            total: result.rows.length,
          },
        },
      };
    } catch (error) {
      console.error('Error querying rolleiflex_db:', error);
      ctx.throw(500, 'Internal Server Error');
    } finally {
      await client.end();
    }
  },

  async findOne(ctx) {
    const { id } = ctx.params;

    const client = new Client({
      host: '127.0.0.1',
      port: 5432,
      database: 'rolleiflex_db',
      user: 'rolleiflex',
      password: 'idcc8Wv3kpHjnNLpaoKKyhLYaYEWJr49',
    });

    try {
      await client.connect();

      const result = await client.query('SELECT * FROM rolleiflex_cameras WHERE id = $1', [id]);

      if (result.rows.length === 0) {
        ctx.throw(404, 'Serial number not found');
      }

      const row = result.rows[0];
      return {
        data: {
          id: row.id,
          attributes: {
            serial_start: row.serial_start,
            serial_end: row.serial_end,
            model_name: row.model_name,
            year_produced: row.year_produced,
            taking_lens: row.taking_lens,
            looking_lens: row.looking_lens,
            description: row.description,
          },
        },
        meta: {},
      };
    } catch (error) {
      console.error('Error querying rolleiflex_db:', error);
      ctx.throw(500, 'Internal Server Error');
    } finally {
      await client.end();
    }
  },
};
