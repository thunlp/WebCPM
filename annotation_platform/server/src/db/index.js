const { MongoClient } = require('mongodb');
const config = require('../../../config.json');

// Connection URL
const client = new MongoClient(config.server.database.url);

// Database Name
const dbName = 'bereco';

let conn;

async function main() {
  // Use connect method to connect to the server
  await client.connect();
  console.log('DB Connected.');
  const db = client.db(dbName);

  conn = db;

  // db.collection()

  return db;
}

module.exports = {
  connect: main,
  getCollection: (coll) => {
    return conn.collection(coll);
  },
};
