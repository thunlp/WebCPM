// c6b6124396ea4ba395905e0ed8cab526
// 972aadf78f6243ae9f5832dda6f8433b
// https://api.bing.microsoft.com/

const axios = require('axios').default;

const SUBSCRIPTION_KEY = 'c6b6124396ea4ba395905e0ed8cab526'

axios.get('https://api.bing.microsoft.com/v7.0/search', {
  params: {
    q: '123',
    mkt: 'zh-CN',
    responseFilter: 'webPages',
    freshness: 'day',
    count: 20,
  },
  headers: {
    'Ocp-Apim-Subscription-Key': SUBSCRIPTION_KEY,
  },
}).then((res) => {
  console.log(res.data.webPages.value.map((item) => {
    return {
      title: item.name,
      href: item.url,
      summary: item.snippet,
    };
  }));
});
