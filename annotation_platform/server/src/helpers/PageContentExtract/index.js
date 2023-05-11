const { getBrowser } = require('../index');

const sleep = (time) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve();
    }, time);
  });
}

class PageContentExtract {
  #url = '';

  constructor(url) {
    this.#url = url;
  }

  async extract() {
    const browser = await getBrowser();

    const page = await browser.newPage();

    await Promise.race([
      page.goto(this.#url),
      new Promise((resolve) => {
        setTimeout(() => {
          resolve();
        }, 4000);
      }),
    ])

    await page.click('html');

    await sleep(1000);

    await page.keyboard.down('a');

    await sleep(30);

    await page.keyboard.down('a');

    await sleep(30);

    await page.keyboard.down('a');

    try {
      await sleep(30);

      await page.click('body');

      await sleep(30);

      await page.click('sr-highlight-ctl.done');
    } catch {}

    const html = await page.$eval('.simpread-read-root', el => el.innerHTML);

    // await page.close();

    await browser.close();

    return html;
  }
}

module.exports = PageContentExtract;
