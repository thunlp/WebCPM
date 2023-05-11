const Router = require('koa-router');
const PageContentExtract = require('../../helpers/PageContentExtractFast');

const extractRouter = new Router({
  prefix: '/extract',
});
extractRouter.get('/web', async (ctx) => {
  const { url } = ctx.request.query;

  try {
    const html = await ((new PageContentExtract(url)).extract());

    ctx.body = {
      code: 0,
      message: 'ok',
      data: {
        html,
        href: url,
      },
    };
  } catch (e) {
    ctx.body = {
      code: 1,
      message: '提取内容异常',
      data: {},
    };
  }
});

module.exports = extractRouter;
