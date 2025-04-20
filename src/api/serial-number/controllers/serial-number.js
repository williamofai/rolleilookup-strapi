'use strict';

const { Client } = require('pg');

module.exports = {
  async find(ctx) {
    const client = new Client({
      host: '127.0.0.1',
      port: 5432,
      database: 'rolleiflex_db',
      user: 'rolleiflex',
      password: 'idcc8Wv3kpHjnNLpaoKKyhLYaYEWJr49',
    });

    try {
      await client.connect();
      const result = await client.query('SELECT * FROM rolleiflex_cameras');
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
      console.error('Error querying rolleiflex_db:', error.message);
      ctx.throw(500, `Internal Server Error: ${error.message}`);
    } finally {
      try {
        await client.end();
      } catch (endError) {
        console.error('Error closing database connection:', endError.message);
      }
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

      // Validate ID as a number to prevent SQL injection
      const parsedId = parseInt(id, 10);
      if (isNaN(parsedId)) {
        ctx.throw(400, 'Invalid ID: ID must be a number');
      }

      const result = await client.query('SELECT * FROM rolleiflex_cameras WHERE id = $1', [parsedId]);

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
      console.error('Error querying rolleiflex_db:', error.message);
      // If the error is already a Strapi error (e.g., 400, 404), rethrow it
      if (error.status) {
        throw error;
      }
      // Otherwise, throw a 500 error with the original message
      ctx.throw(500, `Internal Server Error: ${error.message}`);
    } finally {
      try {
        await client.end();
      } catch (endError) {
        console.error('Error closing database connection:', endError.message);
      }
    }
  },

  // Disable create, update, delete operations as the data is read-only
  async create(ctx) {
    ctx.throw(405, 'Method Not Allowed: Create operation is not supported for this read-only API');
  },

  async update(ctx) {
    ctx.throw(405, 'Method Not Allowed: Update operation is not supported for this read-only API');
  },

  async delete(ctx) {
    ctx.throw(405, 'Method Not Allowed: Delete operation is not supported for this read-only API');
  },
};
