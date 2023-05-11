const axios = require('axios').default;
const superagent = require('superagent');
const read = require('node-readability');
const fs = require('fs');

// axios.post('https://api.gugudata.com/news/fetchcontent', {
//   appkey: 'HM8UW6FP9M5V',
//   url: 'https://www.baidu.com/s?wd=%E6%AD%A3%E6%96%87%E5%86%85%E5%AE%B9%E6%8F%90%E5%8F%96%20api&rsv_spt=1&rsv_iqid=0x8e6936b4000f4682&issp=1&f=8&rsv_bp=1&rsv_idx=2&ie=utf-8&rqlang=cn&tn=baiduhome_pg&rsv_dl=tb&rsv_enter=1&oq=%25E9%25A1%25B5%25E9%259D%25A2%25E5%2586%2585%25E5%25AE%25B9%25E6%258F%2590%25E5%258F%2596%2520api&rsv_t=4f31URR3%2BF%2BVAVKCja2v2f6XZerC37dFH0D0XJQ1fFmiarutuBV427UWgiEDk%2Bt8BVFd&rsv_btype=t&inputT=2442&rsv_pq=aec285350004ed15&rsv_sug3=53&rsv_sug1=15&rsv_sug7=100&rsv_sug2=0&rsv_sug4=3018',
//   contentwithhtml: true,
// }).then(res => {
//   console.log(res.data);
//   fs.writeFileSync('./1.html', res.data.Data.Content);
// })

// read('https://baike.baidu.com/item/1/31661?fr=aladdin', (err, result, meta) => {
//   console.log(result)

//   fs.writeFileSync('./1.html', result.html);

// });

// axios.get('https://api.ip138.com/text/', {
//   params: {
//     url: 'https://baike.baidu.com/item/1/31661?fr=aladdin',
//     type: 2,
//     token: '9850021ae618a48eea740a33ca7ebbaf',
//   }
// }).then((res) => {
//   console.log(res.data)
// });

// superagent
//       .post(`https://www.wangmei360.com/user_api.jsp?post_zhengwen`)
//       .send({
//         geturl: 'https://baike.baidu.com/item/1/31661?fr=aladdin',
//       })
//       .end((err, res) => {
//         console.log(err, res)
//       });

const headers = {
  Accept: '*/*',
  'Accept-Encoding': 'gzip, deflate, br',
  'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
  'Cache-Control': 'no-cache',
  Connection: 'keep-alive',
  'Content-Length': '54',
  'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
  Host: 'www.wangmei360.com',
  Origin: 'https://www.wangmei360.com',
  Pragma: 'no-cache',
  Referer: 'https://www.wangmei360.com/tool_getart',
  'sec-ch-ua':
    '" Not A;Brand";v="99", "Chromium";v="96", "Microsoft Edge";v="96"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': 'macOS',
  'Sec-Fetch-Dest': 'empty',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Site': 'same-origin',
  'User-Agent':
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62',
  'X-Requested-With': 'XMLHttpRequest',
};

// axios
//   .post('https://www.wangmei360.com/user_api.jsp?post_zhengwen', {
//     geturl: 'https://blog.csdn.net/studysinklc/article/details/78017330',
//   }, {
//     headers,
//   })
//   .then(res => {
//     console.log(res.data);
//   });

// superagent
//   .post(`https://www.wangmei360.com/user_api.jsp?post_zhengwen`)
//   .set('Origin', 'https://www.wangmei360.com')
//   .set('Referer', 'https://www.wangmei360.com/tool_getart')
//   .send({
//     geturl: 'https://baike.baidu.com/item/1/31661?fr=aladdin',
//   })
//   .end((err, res) => {
//     console.log(err, res)
//   });

// (async() => {
//   const guguResult = await axios.post('https://api.gugudata.com/news/fetchcontent', {
//         appkey: 'HM8UW6FP9M5V',
//         contentwithhtml: true,
//         url: 'https://baike.baidu.com/item/韩国/6009333',
//       });

// console.log(guguResult.data);
// })()

// import Mercury from "@postlight/mercury-parser";
const Merucy = require('@postlight/mercury-parser');
const url =
  'https://baike.baidu.com/item/%E4%B8%AD%E5%8D%8E%E4%BA%BA%E6%B0%91%E5%85%B1%E5%92%8C%E5%9B%BD/106554?fr=aladdin';
Merucy.parse(url).then(result => console.log(result.content));
