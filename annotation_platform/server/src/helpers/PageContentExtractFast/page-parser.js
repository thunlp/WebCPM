const Merucy = require('@postlight/mercury-parser');

module.exports = (url) => {
  console.log(url);
  return new Promise((resolve, reject) => {
    Merucy.parse(url).then((result) => {
      resolve(result.content);
    });
  });
};
