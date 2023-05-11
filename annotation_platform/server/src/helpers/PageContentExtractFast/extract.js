const puppeteer = require('puppeteer');
const axios = require('axios');

let browser;
let page;

const extract = url => {
  console.log(url);
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

    let content = JSON.parse(res).getContent;

    if (content.length < 30) {
      // const guguResult = await axios.post('https://api.gugudata.com/news/fetchcontent', {
      //   appkey: 'HM8UW6FP9M5V',
      //   url: encodeURIComponent(url),
      //   contentwithhtml: true,
      // });
      // console.log(guguResult.data)
      // content = guguResult.data.Data?.Content ?? content;

      const resp = await axios.get('https://api.ip138.com/text/', {
        headers: {
          token: '9850021ae618a48eea740a33ca7ebbaf',
        },
        params: {
          url: encodeURIComponent(url)
        },
      });

      content = resp.data.data.data[1];
    }

    resolve(content);
  });
};

(async () => {
  browser = await puppeteer.launch({
    headless: false,
  });

  page = await browser.newPage();

  await page.goto('https://www.wangmei360.com/tool_getart');
})();

module.exports = {
  extract,
};
