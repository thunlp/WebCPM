const cheerio = require('cheerio');
const superagent = require('superagent');
const { getBrowser } = require('../index');

class BaiduSearchEngine {
  #kw = '';

  constructor(keyword) {
    this.#kw = keyword;
  }

  async search() {
    const browser = getBrowser();

    const url = `https://www.baidu.com/s?wd=${encodeURIComponent(this.#kw)}`;

    const page = await browser.newPage();

    await page.goto(url);

    const html = await page.$eval('html', el => el.innerHTML);

    page.close();

    return this.filterResult(html);
  }

  filterResult(body) {
    const $ = cheerio.load(body);

    const results = $('.result-op');

    const sets = [];

    results.each((index, item) => {
      if (index === 0) return;

      const $item = cheerio.load(item);

      const title = $item('h3 a').text();
      const href = $item('h3 a').attr('href');
      const summary = $item('.c-font-normal').text() || $item('.c-gap-top-small').first().text() || $item('.op_tb_content').text() || $item('.c-span9').text();

      sets.push({
        title,
        href,
        summary,
      });
    });

    return sets;
  }
}

module.exports = BaiduSearchEngine;
