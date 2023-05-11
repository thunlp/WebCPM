const axios = require('axios').default;
const { tianXingAPI } = require('./tianxing-api');

module.exports = (url) => {
  return new Promise((resolve, reject) => {
    const target = `http://url2api.applinzi.com/demo/article?url=${encodeURIComponent(encodeURI(url))}&fields=next&token=demo&_=1646907389825`;
    console.log(target)
    axios.get(target).then((res) => {
      resolve(res.data.content);
    })
    .catch(e => {
      tianXingAPI(encodeURI(url)).then((res) => {
        console.log(res);
        resolve(res);
      });
    });
  });
};
