# SDK DOC

## DEPs

```shell
# install dependencies
npm i
```

## USAGE & APIs

```js
const Record = require('./src/index.js');

const record1 = new Recorder({
  // set debug true will open browser after init
  debug: true,
});

const record2 = new Recorder();
const record3 = new Recorder();
const record4 = new Recorder();
```

```js
// init page
await record.init();

// set topic
await record.setTopic(topic: string);

// bootstrap
await record.start();

// set search keyword
await record.setKeyword(keyword: string);

// do search
await record.search();

// got some result content page
await record.toResult(index: number);

// add an digest to digests list
await record.addDigest(text: string);

// get digest list
const digests = await record.getDigest();

// merge digest by indexes
await record.mergeDigest(idx1, idx2, ...., idxN);

// scroll page up
await record.pageUp();

// scroll page down
await record.pageDown();

// scroll to page top
await record.pageTop();

// returns current result content
// type 0 is search list
// type 1 is search result target content page
const result = await record.getCurrentPageResult();

// get current shown search result list
const currentShownSearchList = await record.getResultDetail();

// get current shown content text
const currentShownContentText = await record.getTargetDetail(withHTML: boolean = false);

// back
await record.back();

// pop an action from op stack
await record.undo();

// reset record
await record.reset();

// over the record
await record.over();
```
