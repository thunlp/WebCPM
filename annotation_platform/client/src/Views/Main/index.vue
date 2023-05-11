<template>
  <div class="main-wrap">
    <header-action
      :max-step="MAX_STEP_COUNT"
      :rest-step="stepCount"
      :app-status="appStatus"
      @toggle-app-status="toggleAppStatus"
    />

    <div class="op-wrap" :style="appStatus === APP_STATUS.CLOSE ? 'opacity: .3;' : ''">
      <div class="overlay" v-if="appStatus === APP_STATUS.CLOSE" />

      <div style="margin-top: -8px; display: flex; justify-content: space-between;">
        <div>
          <a-button type="link" :disabled="!content.length" size="large" @click="doBack">
            <template #icon><LeftOutlined /></template>
            返回({{content.length}})
          </a-button>
          &nbsp;
          <a-input-search
            class="keyword-input"
            placeholder="搜索关键词"
            size="large"
            enter-button
            v-model:value="keyword"
            :onSearch="search"
          />
        </div>

        <div style="margin-right: 12px;">
          <a-button @click="undo">撤销</a-button>
          &nbsp;
          <a-button @click="reset" type="dashed" danger ghost>重置</a-button>
        </div>
        <!-- @search="onSearch" -->
      </div>

      <a-spin :spinning="loading">
        <div class="content-container">
          <div class="left">
            <div>
              <a-card title="浏览内容" class="contents">
                <template #extra>
                  <div style="white-space: nowrap; display: flex; align-items: center">
                    <a-input-search
                      placeholder="内容查找"
                      v-model:value="findKeyword"
                      style="width: 150px; margin-right: 12px"
                      :onSearch="find"
                    />
                    <a-tooltip placement="top">
                      <template #title>
                        <span>下一个</span>
                      </template>
                      <a-button @click="findNext()">
                        <template #icon><DownOutlined /></template>
                      </a-button>
                    </a-tooltip>
                    <a-divider type="vertical" />

                    <a-tooltip placement="top">
                      <template #title>
                        <span>向上翻页</span>
                      </template>
                      <a-button style="margin-right: 8px" @click="scrollUp">
                        <template #icon><VerticalAlignTopOutlined /></template>
                      </a-button>
                    </a-tooltip>

                    <a-tooltip placement="top">
                      <template #title>
                        <span>向下翻页</span>
                      </template>
                      <a-button style="margin-right: 8px" @click="scrollDown">
                        <template #icon><VerticalAlignBottomOutlined /></template>
                      </a-button>
                    </a-tooltip>
                    <div style="margin-right: 8px">
                      <span v-if="isSearchResultPage()">{{curResultChunk + 1}}/{{getCurPageChunkSize() + 1}}</span>
                      <span v-if="isResultContentPage()">{{curTargetPageResultChunk + 1}}/{{getCurPageChunkSize()}}</span>
                    </div>
                    <a-tooltip placement="top">
                      <template #title>
                        <span>回到顶端</span>
                      </template>
                      <a-button @click="scrollToTop">
                        <template #icon><VerticalAlignMiddleOutlined /></template>
                      </a-button>
                    </a-tooltip>
                    </div>
                </template>

                <div class="result-content">
                  <div v-if="isSearchResultPage()">
                    <div v-for="(item, index) in getCurrentResultChunkList()">
                      <div class="result-item">
                        <span class="result-item-title">
                          <strong :class="`result-item-index-${index}`" @click="getPageContent(item.mdurl || item.href)" v-html="item.title" :data-url="item.mdurl || item.href" />
                        </span>

                        <div class="result-item-summary" v-html="item.summary || item.rich" />
                      </div>
                    </div>

                    <div v-if="!getContentStackTop().data.length">
                      无搜索结果
                    </div>
                  </div>

                  <div style="width: 717px" v-if="isResultContentPage()">
                    <!--{{getContentStackTop().data.html}}-->

                    <!--
                    <div v-html="getContentStackTop().data.html" />
                    <div v-html="getCurTargetPageResultChunkText()" />
                    -->
                      <div class="content-container-element" style="width: 717px; word-break: break-all;white-space:pre-wrap;" v-html="getCurTargetPageResultChunkText()"></div>
                    <!--
                      <pre class="content-container-element" style="width: 717px; word-break: break-all;white-space:pre-wrap;">{{getCurTargetPageResultChunkText()}}</pre>
                    <div class="content-container-element-html" />
                    -->
                  </div>

                  <div v-if="!content.length">
                    <div class="center content-tip">
                      暂无内容
                    </div>
                  </div>
                </div>
              </a-card>
            </div>
          </div>

          <div class="right">
            <a-card title="摘要" class="summaries">
              <template #extra>
                <a-button @click="addDigest" type="primary" style="margin-right: 4px;">将选中内容添加到摘要</a-button>
                <a-button @click="mergeDigest">合并摘要</a-button>
              </template>
              <div>
                <a-list item-layout="horizontal" :data-source="digests">
                  <template #renderItem="{ item, index }">
                    <a-list-item>
                      <template #actions>
                        <a-checkbox v-model:checked="item.checked"></a-checkbox>
                        <!-- <a href="javascript:;" @click="rmDigest(item)">删除</a> -->
                        <!-- <a href="javascript:;" @click="changeDigestIndex(item, -1)">上移</a> -->
                        <!-- <a href="javascript:;" @click="changeDigestIndex(item, 1)">下移</a> -->
                      </template>
                      <a-list-item-meta :description="digestDescGetter(item.datas)">
                        <template #title>
                          <div style="position: relative;">
                            <span style="position: absolute; left: -24px;">{{index + 1}}</span>
                            <span><div v-for="(t) in item.datas">{{ t.title }}</div></span>
                          </div>
                        </template>
                      </a-list-item-meta>
                    </a-list-item>
                  </template>
                </a-list>
              </div>
            </a-card>
          </div>
        </div>
      </a-spin>
    </div>
  </div>
</template>

<script lang="ts" src="./index.ts"></script>

<style lang="less" scoped>
@import './index.less';
</style>
