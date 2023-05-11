// -------------------------------------------------------------------------
// get select content on page
export const getSelectedText = () => {
  if (window.getSelection) {
    return window.getSelection()!.toString();
  } else if ((document as any).selection) {
    return (document as any).selection.createRange().text;
  }
  return '';
};

// -------------------------------------------------------------------------
// format timestamp to YYYY-MM-DD hh:mm:ss
export const formatTimestamp = (ts = Date.now()) => {
  const date = new Date(ts);

  const YYYY = date.getFullYear().toString().padStart(2, '0');
  const MM = (date.getMonth() + 1).toString().padStart(2, '0');
  const DD = date.getDate().toString().padStart(2, '0');
  const hh = date.getHours().toString().padStart(2, '0');
  const mm = date.getMinutes().toString().padStart(2, '0');
  const ss = date.getSeconds().toString().padStart(2, '0');

  return `${YYYY}-${MM}-${DD} ${hh}:${mm}:${ss}`;
};

// -------------------------------------------------------------------------
// gotten random string
export const randomString = (): string => {
  return Math.random().toString(16).substring(2);
};
