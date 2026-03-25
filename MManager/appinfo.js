/**
 * アプリ情報取得ユーティリティ
 *
 * アプリ内 WebView → window.__APP_INFO__ から取得（JS注入済み）
 * ブラウザ直接アクセス → iTunes Lookup API から最新バージョンを取得
 */

const APP_STORE_ID = '6758864044';
const APP_STORE_COUNTRY = 'jp';

function getAppInfo() {
  return new Promise(function(resolve) {
    // アプリ内 WebView の場合（JS注入済み）
    if (window.__APP_INFO__ && window.__APP_INFO__.isApp) {
      resolve(window.__APP_INFO__);
      return;
    }

    // ブラウザの場合 → App Store API から最新バージョン取得
    fetch('https://itunes.apple.com/lookup?id=' + APP_STORE_ID + '&country=' + APP_STORE_COUNTRY)
      .then(function(res) { return res.json(); })
      .then(function(data) {
        if (data.results && data.results.length > 0) {
          var app = data.results[0];
          resolve({
            version: app.version || '-',
            build: '-',
            ios: '-',
            device: '-',
            isApp: false,
            appName: app.trackName || '家計簿'
          });
        } else {
          resolve(null);
        }
      })
      .catch(function() {
        resolve(null);
      });
  });
}

/**
 * mailto リンクにアプリ情報を付加
 */
function buildMailtoHref(info) {
  var subject = encodeURIComponent('【家計簿】お問い合わせ');
  var BR = '\r\n';
  var lines = [BR, BR, '--------------------', 'アプリ情報（削除しないでください）'];

  if (info.isApp) {
    lines.push('バージョン: ' + info.version + ' (' + info.build + ')');
    lines.push('iOS: ' + info.ios);
    lines.push('デバイス: ' + info.device);
  } else {
    lines.push('バージョン: ' + info.version + ' (App Store)');
    lines.push('環境: ブラウザからのお問い合わせ');
  }

  lines.push('--------------------');
  var body = encodeURIComponent(lines.join(BR));
  return 'mailto:lj_dev@ymail.ne.jp?subject=' + subject + '&body=' + body;
}
