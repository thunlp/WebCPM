# WebCPM, temporary codes for the platform, we would soon push an upgraded version of the platform.

## usage

### env required

- Node.js
- MongoDB

### init config

```shell
npm run config
```

### client

```shell
cd ./client

npm i

# develop
# visit on http://localhost:3000
npm run dev

# build
# output `/server/public`
npm run build
```

### server

```shell
cd ./server
npm i

# develop
# default listen on 3000 port
npm run dev

# prod
# start server
npm start
# stop server
npm stop
```

### third part api

- [tian api](https://www.tianapi.com/apiview/66)

  page content extract service

- [bing search api](https://www.microsoft.com/en-us/bing/apis/bing-web-search-api)

  search service

## config

```json
{
  "server": {
    // 服务端监听端口
    "port": 3001,
    // 是否使用数据库
    // 如果不使用数据库，GET:/record接口也无法使用
    "useDatabase": false,
    // 是否将每次结果保存为本地文件
    // 目录 /server/db/*.json
    "storeResultJSON": false,
    // 数据库配置
    "database": {
      "url": "mongodb://localhost:27017"
    },
    // API密钥
    "keys": {
      "bingAPI": "",
      "tianAPI": ""
    }
  },
  "client": {
    // 客户端服务
    "devServer": {
      "port": 3000
    },
    "env": {
      // 是否保留用于还原的状态
      "NEED_COVER_ACTION": false,
      // 服务端接口前缀
      "DOMAIN": "",
      // 搜索结果过滤哪些域名
      "SEARCH_SITE_FILTER": []
    }
  }
}
```

## Deploy

``` shell
# init config
npm run config

# build and run service
npm run build && npm start
```

## APIs

### search

```shell
search keyword

PATH:
  /search

METHOD:
  GET

PARAMS:
  - engine
    search engine, got one of 'bing'|'360'|'baidu'
  - keyword
    search keyword, got string
  - filters
    filter option, got JSON string: { "domain": ["domain1.com", "domain2.cn", "x.domain.cn"] }
```

### extract

``` shell
extract WEB main content

PATH:
  /extract/web

METHOD:
  GET

PARAMS:
  - url
    URL to extract, got string
```

### record

```shell
record all of user actions(store to DB)

PATH:
  /record/action

METHOD:
  POST

PARAMS:
  - JSON BODY
    all of body will store to DB
```

```shell
PATH:
  /record

METHOD:
  GET

PARAMS:
  - start
    how many data will be skip, got number
  - count
    wanna get how many data, got number

  - topic
    question number, got string
```
