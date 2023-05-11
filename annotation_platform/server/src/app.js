const Koa = require('koa');
const Body = require('koa-body');
const path = require('path');
const Cors = require('koa-cors');
const recordRouter = require('./routes/record');
const extractRouter = require('./routes/extract');
const searchRouter = require('./routes/search');
const static = require('koa-static');
const bodyParser = require('koa-bodyparser');
const config = require('../../config.json');

const app = new Koa();

app.use(Cors());
app.use(static(path.resolve(__dirname, '../public')));
app.use(Body({
  jsonLimit: '100mb',
  formLimit: '100mb',
  textLimit: '100mb',
  json: true,
  formidable: {
    maxFieldsSize: 100 * 1024 * 1024,
  },
}));

app.use(bodyParser({
  formLimit:"10mb",
  jsonLimit:"10mb"
}));

app.use(searchRouter.routes());
app.use(extractRouter.routes());
app.use(recordRouter.routes());

if (config.server.useDatabase) {
  require('./db/index').connect().then(() => {
    app.listen(config.server.port);
  });
} else {
  console.log(233);
  app.listen(config.server.port);
}
