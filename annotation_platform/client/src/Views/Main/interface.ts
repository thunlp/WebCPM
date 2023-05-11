export enum CONTENT_TYPE {
  SEARCH_RESULT,
  RESULT_TARGET_PAGE,
}

export interface ContentItem {
  type: CONTENT_TYPE;
  data: any;
}

export interface DigestData {
  title: string;
  desc: string;
  chunkIndex: number;
}[]

export interface Digest {
  datas: DigestData[];
  checked: boolean;
}

export interface Operate {
  state: any;
  undo: (args: {
    op: Operate;
  }) => void;
}

export enum APP_STATUS {
  OPEN,
  CLOSE,
}
