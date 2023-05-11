const puppeteer = require('puppeteer');

let browser;
let page;

const extract = url => {
  return new Promise(async (resolve, reject) => {
    const res = await page.evaluate(async (url) => {
      return await (
        await fetch('https://www.wangmei360.com/user_api.jsp?post_zhengwen', {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
          },
          method: 'POST',
          body: `geturl=${encodeURIComponent(url)}`,
        })
      ).text();
    }, url);

    resolve(res);
  });
};

(async () => {
  browser = await puppeteer.launch({
    headless: true,
  });

  page = await browser.newPage();

  await page.goto('https://www.wangmei360.com/tool_getart');
})();

module.exports = {
  extract,
};
