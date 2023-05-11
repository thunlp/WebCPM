const axios = require('axios').default;
const config = require('../../../../config.json');

const tianXingAPI = async (url) => {
  const res = await axios.get('http://api.tianapi.com/htmltext/index', {
    params: {
      key: config.server.keys.tianAPI,
      url,
    },
  });

  // console.log(res.data)

  try {
    return res.data.newslist[0].content;
  } catch (e) {
    return '内容提取失败，请重试';
  }
};

module.exports = {
  tianXingAPI,
};
