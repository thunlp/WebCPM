const Recorder = require('../src/index');

const r = new Recorder({
  // set debug true will open browser after init
  debug: true,
});

(async () => {
  await r.init({
    debug: true,
  });
  await r.setTopic('a3c');

  setTimeout(async () => {
  await r.start();
  await r.setKeyword('ddd');
  await r.over();
  }, 5000)

})();

