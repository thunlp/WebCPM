// https://www.so.com/s?q=%E8%8D%89%E6%96%99%E4%BA%8C%E7%BB%B4%E7%A0%81

const cheerio = require('cheerio');
const superagent = require('superagent');

const sleep = (time) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve();
    }, time);
  });
}

class QH360SearchEngine {
  #kw = '';

  constructor(keyword) {
    this.#kw = keyword;
  }

  request(kw = this.#kw, page = 1) {
    return new Promise((resolve, reject) => {
      superagent
        .get(`https://www.so.com/s?q=${kw}&pn=${page}`)
        .end((err, res) => {
          if (err) {
            reject(err);
            return;
          }

          const body = res.text;

          resolve(this.filterResult(body));
        });
    });
  }

  search() {
    return new Promise(async (resolve, reject) => {
      let res = [];
      for (let i = 1; i <= 4; i++) {
        res = [
          ...res,
          ...await this.request(this.#kw, i),
        ];
        await sleep(300);
      }

      resolve(res);
    });
  }

  filterResult(body) {
    const $ = cheerio.load(body);

    const results = $('.result .res-list');

    const sets = [];

    results.each((index, item) => {
      const $item = cheerio.load(item);

      const title = $item('.res-title ').text();
      const href = $item('a').attr('href');
      const mdurl = $item('a').attr('data-mdurl');
      const rich = $item('.res-rich').text();
      const summary = $item('.res-desc').text();

      sets.push({
        title,
        href,
        summary,
        rich,
        mdurl,
      });
    });

    return sets;
  }
}

module.exports = QH360SearchEngine;
