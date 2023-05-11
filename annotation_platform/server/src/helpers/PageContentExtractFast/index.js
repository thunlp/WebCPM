// const { extract } = require('./extract');
const pageParser = require('./page-parser');
const { tianXingAPI } = require('./tianxing-api');
const applinzi = require('./applinzi');

class PageContentExtract {
  #url = '';

  constructor(url) {
    this.#url = url;
  }

  extract() {
    return applinzi(this.#url);

    // return tianXingAPI(encodeURI(this.#url));
    // return pageParser(encodeURI(this.#url));
  }
}

module.exports = PageContentExtract;
