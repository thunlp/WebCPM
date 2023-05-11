const puppeteer = require('puppeteer');
const path = require('path');

const SIMPLE_READ_WELCOME_HREF = 'chrome-extension://ijllcpnolfcooahcekpamkbidhejabll/options/options.html';

const closeSimpleReadWelcome = async (browser) => {
  return new Promise((resolve) => {
    const timer = setInterval(async () => {
      const pages = await browser.pages();

      for (let i = 0; i < pages.length; i++) {
        const page = pages[i];

        const url = await page.url();

        if (url.startsWith(SIMPLE_READ_WELCOME_HREF)) {
          await page.close();
          clearInterval(timer);
          resolve();
          break;
        }
      }
    }, 300);
  });
};

const initHeadlessBrowser = () => {
  puppeteer.launch({
    headless: false,
    // headless: false,
    args : [`--disable-extensions-except=${path.resolve(__dirname, './PageContentExtract/ext/simpleread/2.2.0.520_0')}`]
  }).then((b) => {
    browser = b;

    closeSimpleReadWelcome(browser);
  });
};

// initHeadlessBrowser();

module.exports = {
  getBrowser: async () => {
    const browser = await puppeteer.launch({
      headless: false,
      // headless: false,
      args : [`--disable-extensions-except=${path.resolve(__dirname, './PageContentExtract/ext/simpleread/2.2.0.520_0')}`]
    });

    await closeSimpleReadWelcome(browser);

    return browser;
  },
};
