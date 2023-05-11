const Router = require('koa-router');
const url = require('url');
const BingSearchEngine = require('../../helpers/BingSearchEngine');
const QH360SearchEngine = require('../../helpers/360SearchEngine');

const searchRouter = new Router({
  prefix: '/search',
});
searchRouter.get('/', async (ctx) => {
  const { engine, keyword, filters } = ctx.request.query;

  const filterDomain = filters ? ((JSON.parse(filters)).domain || []) : []

  let res = [];
  if (engine === 'bing') {
    res = await ((new BingSearchEngine(keyword)).searchAPI());

    res = (res || []).filter(({ href = '' }) => {
      return !filterDomain.some((domain) => {
        const host = url.parse(href).host;
        console.log(host, domain , domain.includes(host))
        return host.includes(domain);
      });
    });

    res.length = Math.min(res.length, 25);
  } else if (engine === '360') {
    res = await ((new QH360SearchEngine(keyword)).search());
  } else if (engine === 'baidu') {
    res = await ((new BaiduSearchEngine(keyword)).search());
  }

  ctx.body = {
    code: 0,
    message: 'ok',
    data: res,
  }
});

module.exports = searchRouter;
