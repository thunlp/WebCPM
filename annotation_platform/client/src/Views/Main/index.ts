import { ref, defineComponent } from 'vue';
import HeaderAction from './components/HeaderAction/index.vue';
import { message, Modal } from 'ant-design-vue';
import $ from 'jquery';
import { chunk, isArray } from 'lodash';
import {
  Digest,
  CONTENT_TYPE,
  ContentItem,
  APP_STATUS,
  DigestData,
  Operate,
} from './interface';
import {
  SearchOutlined,
  LeftOutlined,
  VerticalAlignTopOutlined,
  VerticalAlignBottomOutlined,
  VerticalAlignMiddleOutlined,
  DownOutlined,
} from '@ant-design/icons-vue';
import {
  searchBing,
  getPageContent as _getPageContent,
  recordAction,
} from '../../service';
import {
  formatTimestamp,
  getSelectedText,
  randomString,
} from '../../helpers/utils';
import FindControl from '../../helpers/handler/FindControl';
import { urlFilter } from './helpers/urlFilter';
import config from '../../../../config.json';

// -------------------------------------------------------------------------
// constants

// init step total
const MAX_STEP_COUNT = 100;
// scroll content class attr val
const SCROLL_CONTENT_CLASS = 'result-content';
// position whit scroll action
const SCROLL_OFFSET = 100;
// search result list chunk size
const SEARCH_RESULT_LIST_CHUNK_SIZE = 3;
// result target page text chunk content length
const RESULT_TARGET_PAGE_PER_TEXT_COUNT = 500;

// -------------------------------------------------------------------------
// component script
export default defineComponent({
  components: {
    HeaderAction,
    SearchOutlined,
    LeftOutlined,
    VerticalAlignBottomOutlined,
    VerticalAlignTopOutlined,
    VerticalAlignMiddleOutlined,
    DownOutlined,
  },

  setup() {
    // -------------------------------------------------------------------------
    // -------------------------------------------------------------------------
    // refs
    // -------------------------------------------------------------------------
    // -------------------------------------------------------------------------

    // app status
    const appStatus = ref(APP_STATUS.CLOSE);
    // search keyword
    const keyword = ref('');
    // page stack
    const content = ref<ContentItem[]>([]);
    // recorded digests
    const digests = ref<Digest[]>([]);
    // step count
    const stepCount = ref(MAX_STEP_COUNT);
    // content loading status
    const loading = ref(false);
    // find keyword
    const findKeyword = ref('');
    // find controller
    const findController = ref<FindControl>(new FindControl());
    // trace id, create when record start
    const traceId = ref('');
    // current result chunk index
    const curResultChunk = ref(0);
    // current target page chunk index
    const curTargetPageResultChunk = ref(0);
    // records
    const recordStack = ref<any[]>([]);
    // operate stack
    const ops = ref<Operate[]>([]);
    // store
    const topic = ref('');

    // -------------------------------------------------------------------------
    // -------------------------------------------------------------------------
    // methods
    // -------------------------------------------------------------------------
    // -------------------------------------------------------------------------

    // -------------------------------------------------------------------------
    // gotten the top in content stack
    const getContentStackTop = (): ContentItem => {
      return content.value[content.value.length - 1] || {};
    };

    // -------------------------------------------------------------------------
    const isResultContentPage = () => {
      return getContentStackTop().type === CONTENT_TYPE.RESULT_TARGET_PAGE;
    };

    // -------------------------------------------------------------------------
    const isSearchResultPage = () => {
      return getContentStackTop().type === CONTENT_TYPE.SEARCH_RESULT;
    };

    // -------------------------------------------------------------------------
    const getDigestsUpperData = (): DigestData => {
      return JSON.parse(
        JSON.stringify(
          digests.value.map(item => {
            return item.datas;
          }),
        ),
      );
    };

    // -------------------------------------------------------------------------
    const addOp = (op?: Operate) => {
      op = op || ({} as Operate);

      op.state = {
        ...JSON.parse(JSON.stringify(op?.state ?? {})),
        ...{
          digests: digests.value,
          content: content.value,
          keyword: keyword.value,
          loading: loading.value,
          findKeyword: findKeyword.value,
          // recordStack: [...recordStack.value],
          stepCount: stepCount.value,
          curResultChunk: curResultChunk.value,
          curTargetPageResultChunk: curTargetPageResultChunk.value,
          // @ts-ignore
          topic: window.__getTopic(),
          appStatus: appStatus.value,
        },
      };

      op.undo = op.undo || (({ op }) => {
        const { state } = op;

        digests.value = state.digests;
        content.value = state.content;
        keyword.value = state.keyword;
        loading.value = state.loading;
        findKeyword.value = state.findKeyword;
        // recordStack.value = state.recordStack;
        stepCount.value = state.stepCount;
        curResultChunk.value = state.curResultChunk;
        curTargetPageResultChunk.value = state.curTargetPageResultChunk;
        topic.value = state.topic;
        // @ts-ignore
        window.__setTopic(state.topic);
        appStatus.value = state.appStatus;
      });

      ops.value.push(op);
    };

    // -------------------------------------------------------------------------
    // undo
    const undo = () => {
      if (!ops.value.length) {
        message.info('没有可以撤销的步骤');
        return;
      }

      if (ops.value.length === 1) {
        message.info('已经是最前一步了');
        return;
      }

      const op = ops.value.pop();

      op?.undo({
        op,
      });
    };

    // -------------------------------------------------------------------------
    // make steps decrease progressively
    const minusStep = (count = -1) => {
      stepCount.value = stepCount.value + count;

      if (stepCount.value <= 0) {
        toggleAppStatus();
        message.info('操作步骤达到上限，自动结束本次数据收集');
      }
    };

    // -------------------------------------------------------------------------
    // set loading status active
    const openLoading = () => {
      loading.value = true;
    };

    // -------------------------------------------------------------------------
    // set loading status lazy
    const closeLoading = () => {
      loading.value = false;
    };

    // -------------------------------------------------------------------------
    // for pop action
    const popContentStack = () => {
      content.value.pop();
    };

    // -------------------------------------------------------------------------
    // basic record info, each record has those info
    const getRecordMeta = (): {
      keyword: string;
      triggerAt: number;
      stackLength: number;
      step: number;
      traceId: string;
      currentPageInfo: {
        title: string;
        href: string;
        type: string | number;
        scrollTop: number | string;
      };
    } => {
      const stack = getContentStackTop();

      return {
        keyword: keyword.value,
        triggerAt: Date.now(),
        stackLength: content.value.length,
        step: MAX_STEP_COUNT - stepCount.value,
        traceId: traceId.value,
        currentPageInfo: {
          title: stack?.data?.title ?? '',
          type: stack?.type ?? '',
          href: stack?.data?.href ?? '',
          scrollTop: $(`.${SCROLL_CONTENT_CLASS}`).scrollTop() || 0,
        },
      };
    };

    // -------------------------------------------------------------------------
    // get current page content
    const getCurPageContent = () => {
      if (isSearchResultPage()) {
        return getCurrentResultChunkList();
      } else {
        return getCurTargetPageResultChunkText();
      }
    };

    // -------------------------------------------------------------------------
    // do record action
    const record = (action: string, details: any = {}) => {
      recordStack.value.push({
        action,
        details,
        pageContentInViewport: getCurPageContent(),
        digests: getDigestsUpperData(),
        ...config.client.env.NEED_COVER_ACTION
          ? {
            operateStack: [...ops.value],
          }
          : {},
        ...getRecordMeta(),
      });
      // recordAction({
      //   action,
      //   details,
      //   ...getRecordMeta(),
      // });
    };

    // -------------------------------------------------------------------------
    // search keyword
    const search = async (domainFilter: string[]) => {
      addOp();

      openLoading();

      try {
        const res = await searchBing(keyword.value, {
          domain: isArray(domainFilter) ? domainFilter : config.client.env.SEARCH_SITE_FILTER,
        });

        closeLoading();

        content.value = [];

        res.data = urlFilter(res.data);

        content.value.push({
          type: CONTENT_TYPE.SEARCH_RESULT,
          data: res.data,
        });
        curResultChunk.value = 0;

        minusStep();
        record('PRESS_SEARCH', {
          keyword: keyword.value,
          result: res.data,
        });
      } catch (e) {}
    };

    const eachCurrentResultChunkIndex = (callback: Function) => {
      const start = curResultChunk.value * SEARCH_RESULT_LIST_CHUNK_SIZE;
      const end = start + SEARCH_RESULT_LIST_CHUNK_SIZE;

      for (let i = start; i < end; i++) {
        callback(i);
      }
    };

    const getCurrentResultDeepClone = () => {
      return JSON.parse(JSON.stringify(getContentStackTop()));
    };

    // -------------------------------------------------------------------------
    // get current result chunk lint content
    const getCurrentResultChunkList = () => {
      const res: any[] = [];

      const top = getContentStackTop();

      eachCurrentResultChunkIndex((i: number) => {
        if (top.data[i]) {
          res.push(top.data[i]);
        }
      });

      return res;
    };

    const getCurrentResultChunkListDeep = () => {
      return JSON.parse(JSON.stringify(getCurrentResultChunkList()));
    };

    // -------------------------------------------------------------------------
    // extract page content by page URL
    const getPageContent = async (url: string): Promise<void> => {
      addOp();

      loading.value = true;
      const res = await _getPageContent(url);
      loading.value = false;

      if (res.code === 0) {
        const html = chunk(
          $(
            `<div>${res.data.html}</div>`.replace(
              /<\/(div|p)>/gim,
              '</div>!!--break-line--!!',
            ),
          )
            .text()
            .replace(/\s+/gim, ' ')
            .replace(/<\/?.+?>/gim, ' ')
            .replace(/[\r\n]/gim, '\n')
            .replace(/!!--break-line--!!/gim, '<br />'),
          RESULT_TARGET_PAGE_PER_TEXT_COUNT,
        ).map(item =>
          [...new Set(item.join('').split('<br />'))].join('<br />'),
        );

        content.value.push({
          type: CONTENT_TYPE.RESULT_TARGET_PAGE,
          data: {
            html,
            href: res.data.href,
          },
        });

        curTargetPageResultChunk.value = 0;

        minusStep();

        record('LOAD_PAGE_DETAIL', {
          href: url,
          pageMainContent: html,
        });
      } else {
        message.error(res.message);
      }
    };

    // -------------------------------------------------------------------------
    // get current target page result chunk content
    const getCurTargetPageResultChunkText = (idx?: number, html = true) => {
      const top = getContentStackTop();

      if (!top.data) return;

      const content = top.data.html[idx || curTargetPageResultChunk.value];

      try {
        if (!html) {
          return $.trim($(`<div>${content}</div>`).text());
        }
      } catch (err) {
        console.error(err);
      }

      return $.trim(content);
    };

    // -------------------------------------------------------------------------
    // record selection text
    const addDigest = (text: string) => {
      addOp();

      text = text || getSelectedText();

      if (typeof text !== 'string') {
        text = getSelectedText();
      }

      if (!text) {
        message.info('无选中内容');
        return false;
      }

      if (!isResultContentPage()) {
        message.info('请在内容详情页标注');
        return false;
      }

      digests.value.push({
        datas: [
          {
            title: `${formatTimestamp()}`,
            desc: text,
            chunkIndex: curTargetPageResultChunk.value,
            // top.type === CONTENT_TYPE.SEARCH_RESULT
            //   ? curResultChunk.value
            //   : curTargetPageResultChunk.value,
          },
        ],
        checked: false,
      });

      minusStep();

      record('ADD_DIGEST', {
        text,
      });

      return true;
    };

    // -------------------------------------------------------------------------
    // be init
    const beInitStatus = () => {
      content.value = [];
      keyword.value = '';
      digests.value = [];
      loading.value = false;
      findKeyword.value = '';
      recordStack.value = [];
      findController.value = new FindControl();
      traceId.value = '';
      stepCount.value = MAX_STEP_COUNT;
      topic.value = '';
    };

    const reset = () => {
      Modal.confirm({
        okText: '确认重置',
        cancelText: '取消',
        title: '确定重置吗？',
        onOk() {
          beInitStatus();
        },
      });
    };

    // -------------------------------------------------------------------------
    // toggle app status
    const toggleAppStatus = () => {
      addOp();

      if (appStatus.value === APP_STATUS.OPEN) {
        // when record start
        appStatus.value = APP_STATUS.CLOSE;

        record('RECORD_CLOSE', {
          digests: getDigestsUpperData(),
        });

        message.warn('正在上传记录数据');

        const recordContent = {
          topic: topic.value,
          userAgent: navigator.userAgent,
          actions: recordStack.value,
          digests: digests.value,
          tractId: traceId.value,
          createdAt: Date.now(),
        };

        loading.value = true;
        console.log(recordContent);

        recordAction(recordContent).then(() => {
          message.success('记录数据上传成功');
          beInitStatus();
        }).catch((err) => {
          beInitStatus();
          message.error(err.message);
        });


        return recordContent;
      } else {
        // when record end
        appStatus.value = APP_STATUS.OPEN;

        traceId.value = `${randomString()}${randomString()}`;

        // @ts-ignore
        topic.value = window.__getTopic();

        record('RECORD_START', {});
      }
    };

    // -------------------------------------------------------------------------
    // to scroll result content to current top plus offset
    const scrollResultContent = (offset: number) => {
      const $el = $(`.${SCROLL_CONTENT_CLASS}`);

      $el[0].scrollTo(0, $el.scrollTop()! + offset);
    };

    // -------------------------------------------------------------------------
    // page scroll top minus
    const scrollUp = () => {
      if (isSearchResultPage()) {
        if (curResultChunk.value <= 0) {
          message.info('已经在顶端了');
          return;
        }
        addOp();
        curResultChunk.value = curResultChunk.value - 1;
      } else if (isResultContentPage()) {
        if (curTargetPageResultChunk.value <= 0) {
          message.info('已经在顶端了');
          return;
        }
        addOp();
        curTargetPageResultChunk.value = curTargetPageResultChunk.value - 1;
      }

      minusStep();

      record('TRIGGER_SCROLL_UP');

      setTimeout(() => {
        findController.value = new FindControl();
      });
    };

    // -------------------------------------------------------------------------
    // get current page chunk size
    const getCurPageChunkSize = () => {
      const top = getContentStackTop();

      if (isSearchResultPage()) {
        return Math.ceil(top.data.length / SEARCH_RESULT_LIST_CHUNK_SIZE) - 1;
      } else if (isResultContentPage()) {
        return top.data.html.length;
      }

      return 0;
    };

    // -------------------------------------------------------------------------
    // page scroll top plus
    const scrollDown = () => {
      const top = getContentStackTop();

      if (isSearchResultPage()) {
        if (
          curResultChunk.value >=
          Math.ceil(top.data.length / SEARCH_RESULT_LIST_CHUNK_SIZE) - 1
        ) {
          message.info('最后一页了');
          return;
        }
        addOp();
        curResultChunk.value = curResultChunk.value + 1;
      } else if (isResultContentPage()) {
        if (curTargetPageResultChunk.value >= top.data.html.length - 1) {
          message.info('最后一页了');
          return;
        }
        addOp();
        curTargetPageResultChunk.value = curTargetPageResultChunk.value + 1;
      }

      minusStep();

      record('TRIGGER_SCROLL_DOWN');

      setTimeout(() => {
        findController.value = new FindControl();
      });
    };

    // -------------------------------------------------------------------------
    // scroll to top
    const scrollToTop = () => {
      if (isSearchResultPage()) {
        if (curResultChunk.value === 0) {
          message.info('已经在顶端了');
          return;

        }
        addOp();

        curResultChunk.value = 0;
      } else if (isResultContentPage()) {
        if (curTargetPageResultChunk.value === 0) {
          message.info('已经在顶端了');
          return;
        }
        addOp();

        curTargetPageResultChunk.value = 0;
      }

      minusStep();

      record('TRIGGER_SCROLL_TO_TOP');
    };

    // -------------------------------------------------------------------------
    // pop content stack, its mean back action
    const doBack = () => {
      addOp();

      popContentStack();

      minusStep();

      record('PAGE_GO_BACK');
    };

    // -------------------------------------------------------------------------
    // find
    const find = () => {
      const top = JSON.parse(JSON.stringify(getContentStackTop()));

      //   ? curResultChunk.value
      //   : curTargetPageResultChunk.value,

      if (isSearchResultPage()) {
        // let firstHave = -1;

        // top.data.forEach((item: any, index: number) => {
        eachCurrentResultChunkIndex((index: number) => {
          const item = top.data[index];

          const [titleHas, replacedTitle] = FindControl.replaceSearchText(
            item.title,
            findKeyword.value,
          );
          const [summaryHas, replacedSummary] = FindControl.replaceSearchText(
            item.summary,
            findKeyword.value,
          );

          item.title = replacedTitle;
          item.summary = replacedSummary;

          // if (titleHas || summaryHas) {
          //   firstHave = index;
          // }
        });

        // if (firstHave > -1) {
        //   curResultChunk.value = Math.floor(
        //     firstHave / SEARCH_RESULT_LIST_CHUNK_SIZE,
        //   );
        // }
      } else if (isResultContentPage()) {
        // for (let i = 0, len = top.data.html.length;)
        const replaced: string[] = [];
        // let firstIndex = -1;

        const item = top.data.html[curTargetPageResultChunk.value];

        // top.data.html.forEach((item: any, index: number) => {
        const [has, replacedChunk] = FindControl.replaceSearchText(
          item,
          findKeyword.value,
        );

        // if (has && firstIndex === -1) {
        //   firstIndex = index;
        // }

        replaced.push(replacedChunk);
        // });

        top.data.html[curTargetPageResultChunk.value] = replacedChunk;
        // top.data.html = replaced;

        // if (firstIndex > -1) {
        //   curTargetPageResultChunk.value = firstIndex;
        // }
      }

      popContentStack();
      content.value.push(top);

      setTimeout(() => {
        // findController.value = new FindControl(top.type === CONTENT_TYPE.RESULT_TARGET_PAGE ? '.content-container-element' : '', findKeyword.value);
        findController.value = new FindControl();

        // record('FIND', {
        //   findKeyword: findKeyword.value,
        //   findIndex: findController.value.currentFocusResultIndex,
        //   findResultLength: findController.value.resultLength,
        // });
      });
    };

    const setKeyword = (kw: string) => {
      keyword.value = kw;
    };

    const setTopic = (topic: string) => {
      // @ts-ignore
      window.__setTopic(topic);
    }

    const open = () => {
      if (appStatus.value === APP_STATUS.OPEN) {
        return false;
      }

      toggleAppStatus();

      return true;
    };

    const over = () => {
      if (appStatus.value === APP_STATUS.CLOSE) {
        return false;
      }

      const data = toggleAppStatus();

      return JSON.parse(JSON.stringify(data));
    };

    const selectRange = () => {
      // const selection = window.getSelection();
      // selection.removeAllRanges();
      // const range = document.createRange();
      // const node = document.querySelector(".content-container-element");
      // range.selectNodeContents(node); // 需要选中的dom节点
      // selection.addRange(range);
    }


    // -------------------------------------------------------------------------
    // find next
    const findNext = () => {
      findController.value.next({
        elementClassName: SCROLL_CONTENT_CLASS,
      });

      // record('FIND_NEXT', {
      //   findKeyword: findKeyword.value,
      //   findIndex: findController.value.currentFocusResultIndex,
      //   findResultLength: findController.value.resultLength,
      // });
    };

    const rmDigest = (item: Digest) => {
      const idx = digests.value.findIndex(i => i === item);

      digests.value.splice(idx, 1);
    };

    const changeDigestIndex = (item: Digest, offset: number) => {
      const idx = digests.value.findIndex(i => i === item);
      const target = digests.value[idx];

      if (idx === 0) {
        message.info('已经在最前了');
        return;
      }

      if (idx === digests.value.length - 1) {
        message.info('已经在最后了');
        return;
      }

      digests.value.splice(idx, 1);
      digests.value.splice(idx + offset, 0, target);
    };

    const digestDescGetter = (item: any) => {
      return item.map((i: any) => i.desc).join('');
    };

    const mergeDigest = (...indexes: number[]) => {
      indexes.forEach((idx) => {
        if (digests.value[idx]) {
          digests.value[idx].checked = true;
        }
      });

      const count = digests.value.reduce((a, b): number => {
        if (b.checked) {
          return a + 1;
        }

        return a;
      }, 0);

      if (count <= 1) {
        message.info('请选择两个以上的摘要进行合并');
        return false;
      }

      addOp();

      let firstSelected: Digest;

      const selectIndex: number[] = [];

      const before = getDigestsUpperData();

      for (let i = 0; i < digests.value.length; i++) {
        const item = digests.value[i];

        if (item.checked) {
          selectIndex.push(i);

          // @ts-ignore
          if (!firstSelected) {
            firstSelected = item;
          } else {
            firstSelected.datas = [...firstSelected.datas, ...item.datas];
          }
        }

        item.checked = false;
      }

      for (let i = selectIndex.length - 1; i >= 1; i--) {
        digests.value.splice(selectIndex[i], 1);
      }

      minusStep();

      record('MERGE_DIGEST', {
        merges: selectIndex,
        before,
        after: getDigestsUpperData(),
      });

      return true;
    };

    const getDigestsValue = () => {
      return JSON.parse(JSON.stringify(digests.value));
    };

    // -------------------------------------------------------------------------
    const coverActions = (_actions: Operate[]) => {
      const actions = JSON.parse(JSON.stringify(_actions));

      const opStack = actions.pop().operateStack;
      console.log(opStack)

      opStack.forEach((op: Operate) => {
        op.undo = () => {
          const state = op.state;

          setTopic(state.topic);
          digests.value = state.digests;
          content.value = state.content;
          keyword.value = state.keyword;
          loading.value = state.loading;
          findKeyword.value = state.findKeyword;
          // recordStack.value = state.recordStack;
          stepCount.value = state.stepCount;
          curResultChunk.value = state.curResultChunk;
          curTargetPageResultChunk.value = state.curTargetPageResultChunk;
          topic.value = state.topic;
          recordStack.value.pop();

          setTimeout(() => {
            appStatus.value = state.appStatus;
          });
        };
      });

      ops.value = opStack;

      undo();
    };

    // -------------------------------------------------------------------------
    // returns

    const operation = {
      CONTENT_TYPE,

      open,
      over,

      setTopic,
      findKeyword,
      keyword,
      setKeyword,
      search,
      find,

      content,
      getContentStackTop,
      popContentStack,
      getCurrentResultChunkList,
      getCurrentResultChunkListDeep,
      getCurTargetPageResultChunkText,

      getPageContent,

      addDigest,
      digests,
      digestDescGetter,
      mergeDigest,
      rmDigest,
      changeDigestIndex,
      getDigestsValue,

      stepCount,
      MAX_STEP_COUNT,

      APP_STATUS,
      appStatus,
      toggleAppStatus,

      scrollUp,
      scrollDown,
      scrollToTop,

      doBack,

      loading,

      findNext,

      curResultChunk,
      getCurrentResultDeepClone,
      curTargetPageResultChunk,
      getCurPageChunkSize,

      isResultContentPage,
      isSearchResultPage,

      reset,
      undo,
      coverActions,

      ops,
    };

    // @ts-ignore
    window.__operation = operation;

    return operation;
  },
});
