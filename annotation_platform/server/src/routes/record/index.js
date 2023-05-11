const Router = require('koa-router');
const fs = require('fs');
const path = require('path');
const { getCollection } = require('../../db');
const config = require('../../../../config.json');

const recordRouter = new Router({
  prefix: '/record',
});

recordRouter.post('/action', async (ctx) => {
  if (config.server.storeResultJSON) {
    fs.writeFileSync(path.resolve(__dirname, `../../../db/${Math.random().toString(16).substring(2)}_${+new Date()}.json`), JSON.stringify(ctx.request.body, undefined, 2));
  }

  if (config.useDatabase) {
    const coll = await getCollection('records');

    coll.insertOne(ctx.request.body);
  }

  ctx.body = {
    code: 0,
    message: 'ok',
    data: '',
  };
});

recordRouter.get('/', async (ctx) => {
  const { start = 0, count = 10, topic } = ctx.request.query;

  try {
    if (topic) {
      const coll = await getCollection('records');

      const one = await coll.find({
        topic,
      }).toArray();

      ctx.body = {
        code: 0,
        message: 'ok',
        data: one,
      };
    } else {
      const coll = await getCollection('records');

      const all = await coll.find().skip(Number(start)).limit(Number(count)).toArray();

      ctx.body = {
        code: 0,
        message: 'ok',
        data: all,
      };
    }
  } catch (e) {
    ctx.body = {
      code: 1,
      message: e.toString(),
      data: [],
    };
  }
});

module.exports = recordRouter;
