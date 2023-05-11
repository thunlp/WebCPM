const axios = require('axios').default;
const qs = require('qs');
const config = require('../../../../config.json');

const SUBSCRIPTION_KEY = config.server.keys.bingAPI

const api = async keyword => {
  console.log(keyword);
  const params = qs.stringify({
    q: keyword,
    mkt: 'zh-CN',
    responseFilter: 'webPages',
    // freshness: 'day',
    count: 60,
  });
  console.log(params);
  const data = await axios.get(
    `https://api.bing.microsoft.com/v7.0/search?${params}`,
    {
      headers: {
        'Ocp-Apim-Subscription-Key': SUBSCRIPTION_KEY,
      },
    },
  );

  return data.data.webPages.value.map(item => {
    return {
      title: item.name,
      href: item.url,
      summary: item.snippet,
    };
  });
};

module.exports = {
  api,
};
