import { message } from 'ant-design-vue';
import $ from 'jquery';

class FindControl {
  // -------------------------------------------------------------------------
  // find element class name
  // for save same class name
  static findElementClassName = '__find-item';

  // -------------------------------------------------------------------------
  // store last find keyword to clean find result
  static lastFindKeyword = '';

  // -------------------------------------------------------------------------
  // clean search result in text
  static clearSearchText = (content: string) => {
    $(`.${FindControl.findElementClassName}`).attr('class', FindControl.findElementClassName);

    const regexp = new RegExp(
      `<span class="${FindControl.findElementClassName}">(.*?)<\/span>`,
      'igm',
    );
    return content.replace(regexp, '$1');
  };

  // -------------------------------------------------------------------------
  // replace search text
  static replaceSearchText = (content: string, replaceText: string): [boolean, string] => {
    if (FindControl.lastFindKeyword) {
      content = FindControl.clearSearchText(content);
    }

    const reg = new RegExp(`${replaceText}`, 'igm');

    const has = reg.test(content);

    if (!has) {
      return [false, content];
    }

    const replaced = content.replace(
      reg,
      `<span class="${FindControl.findElementClassName}">${replaceText}</span>`,
    );

    FindControl.lastFindKeyword = replaceText;

    return [true, replaced];
  };

  // -------------------------------------------------------------------------
  // -------------------------------------------------------------------------
  // props
  // -------------------------------------------------------------------------
  // -------------------------------------------------------------------------

  // find result length
  public resultLength = 0;
  // the index for current focus search result
  public currentFocusResultIndex = 0;

  // -------------------------------------------------------------------------
  // -------------------------------------------------------------------------
  // constructor
  // -------------------------------------------------------------------------
  // -------------------------------------------------------------------------
  constructor(domSelector?: string, replaceText?: string) {
    this.resultLength = $(`.${FindControl.findElementClassName}`).length;
    this.currentFocusResultIndex = -1;

    if (domSelector) {
      const [,html] = FindControl.replaceSearchText($(domSelector).text(), replaceText!);

      // $(`${domSelector}-html`).html(html);
      $(`${domSelector}`).html(html);
      // $(domSelector).html('');
    }

    $.each($(`.${FindControl.findElementClassName}`), (index, item) => {
      $(item).addClass(`${FindControl.findElementClassName}-${index}`);
      $(item).data('top', $(item)[0].offsetTop);

      if (index === ($(`.${FindControl.findElementClassName}`).length - 1)) {
        $(item).addClass(`${FindControl.findElementClassName}-end`);
      }
    });
  }

  // -------------------------------------------------------------------------
  // -------------------------------------------------------------------------
  // methods
  // -------------------------------------------------------------------------
  // -------------------------------------------------------------------------
  public next({
    elementClassName,
  }: {
    elementClassName: string;
  }) {
    this.currentFocusResultIndex = this.currentFocusResultIndex + 1;

    $(`.${FindControl.findElementClassName}`).removeClass(`${FindControl.findElementClassName}-active`);

    const $el = $(`.${FindControl.findElementClassName}-${this.currentFocusResultIndex}`);
    const offsetTop = $el.data('top');

    $el.addClass(`${FindControl.findElementClassName}-active`);

    $(`.${elementClassName}`)[0].scrollTo(0, offsetTop - 91);

    if ($el.hasClass(`${FindControl.findElementClassName}-end`)) {
      message.info('已经是最后一个了');
    }
  }
}

export default FindControl;
