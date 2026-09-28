chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'STORAGE_DATA') {
    chrome.storage.local.set({userStore: message.data}, () => {
      sendResponse({status: 'SUCCESS'});
    });

    // 异步响应，必须返回 true
    return true;
  }
});
