const Puppeteer = require('puppeteer');

const SERVER_HOST = 'http://localhost:3000/';

class Recorder {
  browser;

  // page: Puppeteer.Page;
  page;

  async init({ debug = false } = {}) {
    this.browser = await Puppeteer.launch({
      headless: !debug,
    });

    this.page = await this.browser.newPage()

    await this.page.goto(SERVER_HOST);

    await this.page.waitForSelector('.topic-input');
  }

  // 设置主题
  async setTopic(topic) {
    await this.page.evaluate((topic) => {
      window.__operation.setTopic(topic);
    }, topic);
  }

  // 开始
  async start() {
    await this.page.evaluate(async () => {
      await window.__operation.open();
    });
  }

  // 结束
  async over() {
    return await this.page.evaluate(async () => {
      return await window.__operation.over();
    });
  }

  // 设置关键字
  async setKeyword(keyword) {
    await this.page.evaluate(async (keyword) => {
      await window.__operation.setKeyword(keyword);
    }, keyword);
  }

  // 搜索
  async search() {
    await this.page.evaluate(async () => {
      await window.__operation.search();
    });
  }

  // 进入第几个结果
  async toResult(index) {
    await this.page.evaluate(async (index) => {
      const url = document.querySelector(`.result-item-index-${index}`).getAttribute('data-url');

      await window.__operation.getPageContent(url);
    }, index);
  }

  // 返回
  async back() {
    await this.page.evaluate(async () => {
      await window.__operation.doBack();
    });
  }

  // 添加标注
  async addDigest(text) {
    return await this.page.evaluate(async (text) => {
      return await window.__operation.addDigest(text);
    }, text);
  }

  // 获取标注
  async getDigest() {
    return await this.page.evaluate(() => {
      return window.__operation.getDigestsValue();
    });
  }

  // 合并标注
  async mergeDigest(...indexes) {
    return await this.page.evaluate((indexes) => {
      return window.__operation.mergeDigest(...indexes);
    }, indexes);
  }

  // 撤销
  async undo() {
    return await this.page.evaluate(() => {
      return window.__operation.undo();
    });
  }

  // 重置
  async reset() {
    return await this.page.evaluate(() => {
      return window.__operation.reset();
    });
  }

  // 上一页
  async pageUp() {
    return await this.page.evaluate(() => {
      return window.__operation.scrollUp();
    });
  }

  // 下一页
  async pageDown() {
    return await this.page.evaluate(() => {
      return window.__operation.scrollDown();
    });
  }

  // 到页面顶端
  async pageTop() {
    return await this.page.evaluate(() => {
      return window.__operation.scrollToTop();
    });
  }

  // 获取当前所有搜索结果
  async getCurrentPageResult() {
    return await this.page.evaluate(() => {
      return window.__operation.getCurrentResultDeepClone();
    });
  }

  // 获取当前展现的搜索结果
  async getResultDetail() {
    return await this.page.evaluate(() => {
      return window.__operation.getCurrentResultChunkListDeep();
    });
  }

  // 获取当前详情内容
  async getTargetDetail(html = false) {
    const result = await this.page.evaluate(async (html) => {
      return await window.__operation.getCurTargetPageResultChunkText(undefined, html);
    }, html);

    return result;
  }
}

module.exports = Recorder;
