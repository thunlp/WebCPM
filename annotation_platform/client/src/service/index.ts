import axios from 'axios';
import config from '../../../config.json';

const DOMAIN = config.client.env.DOMAIN;

const getPath = (path: string) => `${DOMAIN}${path}`;

export const searchBaidu = async (keyword: string) => {
  return (await (axios.get(`${getPath('/search')}?keyword=${keyword}&engine=baidu`))).data;
};

export const searchBing = async (keyword: string, filter = {}) => {
  const result = await axios.get(`${getPath('/search')}`, {
    params: {
      keyword,
      engine: 'bing',
      filters: JSON.stringify(filter),
    },
  });

  return result.data;
};

export const getPageContent = async (url: string) => {
  return (await (axios.get(`${getPath('/extract/web')}?url=${url}`))).data;
};

export const recordAction = async (info: any) => {
  // const obj = {
  //   user_agent: navigator.userAgent,
  //   details: {},

  //   ...action,
  // };

  return (await (axios.post(`${getPath('/record/action')}`, info))).data;
};
