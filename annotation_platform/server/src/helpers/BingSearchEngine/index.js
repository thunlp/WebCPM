const cheerio = require('cheerio');
const superagent = require('superagent');
const { getBrowser } = require('../index');
const { api } = require('./api');
const got = require('got');

const SEARCH_PAGES = 2;

class BaiduSearchEngine {
  #kw = '';

  constructor(keyword) {
    console.log(keyword)
    this.#kw = keyword;
  }

  searchAPI() {
    return api(this.#kw);
  }

  async search() {
    // const browser = await getBrowser();

    // const page = await browser.newPage();

    let list = [];

    for (let i = 0; i <= (SEARCH_PAGES - 1); i++) {
      const first = i * 10;

      const url = `https://cn.bing.com/search?q=${encodeURIComponent(this.#kw)}&first=${first}&_=${Date.now()}`;

      // await page.goto(url);

      // const html = await page.$eval('html', el => el.innerHTML);
      const { body: html } = await got.get(url);
      console.log(html)

      list = [
        ...list,
        ...this.filterResult(html),
      ];
    }

    // browser.close();

    return list;
  }

  filterResult(body) {
    const $ = cheerio.load(body);

    const results = $('.b_algo');

    const sets = [];

    results.each((index, item) => {
      const $item = cheerio.load(item);

      const title = $item('.b_title').text();
      const href = $item('a').attr('href');
      const summary = $item('p').text() || $item('.b_vList').text();

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
