import $ from 'jquery';

export const simpleReadFilter = (html: string) => {
  // console.log(html);
  // html = html
  //   .replace(/<sr-annote-floating>.*?<\/sr-annote-floating>/igm, '')
  //   .replace(/<sr-annote-sidebar-bg>.*?<\/sr-annote-sidebar-bg>/igm, '')
  //   .replace(/<toc-bg>.*?<\/toc-bg>/igm, '')
  //   .replace(/<sr-rd-footer-copywrite>.*?<\/sr-rd-footer-copywrite>/igm, '')
  //   .replace(/<sr-rd-crlbar>.*?<\/sr-rd-crlbar>/igm, '')

  // return html;

  // $wrap.find('sr-annote-floating').remove();
  // $wrap.find('sr-annote-sidebar-bg').remove();
  // $wrap.find('toc-bg').remove();
  // $wrap.find('sr-rd-footer-copywrite').remove();
  // $wrap.find('sr-rd-crlbar').remove();

  const $wrap = $(html.replace(/<div>.*><\/div>/igm, '$1\n'));

  $wrap.find('img').remove();

  return $wrap.text();

  // $.each($wrap.find('a'), (index, ele) => {
  //   const $ele = $(ele);

  //   $ele.attr('data-href', $ele.attr('href') || '');

  //   $ele.attr('href', 'javascript:;');
  // });

  // return $wrap[0].outerHTML;
};
