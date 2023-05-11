const blackList = [
  'bilibili.com',
];

export const urlFilter = (list: any[]) => {
  list = JSON.parse(JSON.stringify(list));

  return list.filter((item) => {
    return !blackList.some((url) => {
      return item.href.includes(url);
    });
  });
};
