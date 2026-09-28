let isSelecting = false;
let selectionTimeout;
let mousePosition = {x: 0, y: 0};
let isTranslationPopupVisible = false;

document.addEventListener('mousedown', function (e) {
  if (e.button === 0) {
    isSelecting = true;
    mousePosition.x = e.clientX;
    mousePosition.y = e.clientY;
  }
});
document.addEventListener('mouseup', function (e) {
  if (e.button === 0 && isSelecting) {
    isSelecting = false;
    mousePosition.x = e.clientX;
    mousePosition.y = e.clientY;
    if (selectionTimeout) {
      clearTimeout(selectionTimeout);
    }

    // 鼠标抬起时，首先检查开关状态，再决定是否触发选择处理
    try {
      if (!chrome || !chrome.storage || !chrome.storage.local) {
        console.warn('插件上下文已失效，请刷新页面后重试划词翻译功能。');
        return;
      }

      chrome.storage.local.get(['wordSelectionEnabled'], (result) => {
        if (result.wordSelectionEnabled === false) {
          // 如果明确关闭了划词翻译，则清空选区，并隐藏可能存在的弹窗
          hideOptionsPopup();
          return;
        }
        selectionTimeout = setTimeout(handleTextSelection, 100);
      });
    } catch (e) {
      console.warn('Cannot read extension storage. Extension might be reloaded or context invalidated.', e);
    }
  }
});

(function () {
  if (!window.location.href.startsWith('https://www.momentlingo.cn')) {
    return;
  }

  const userStore = localStorage.getItem('userStore');
  if (!userStore || JSON.parse(userStore).refUserInfo === null) {
    console.log('未找到 userStore 数据');
    return;
  }

  chrome.runtime.sendMessage({type: 'STORAGE_DATA', data: userStore}, resp => {
    if (chrome.runtime.lastError) {
      console.log('消息发送失败 ', chrome.runtime.lastError.message);
      return;
    }
    if (resp.status === 'SUCCESS') {
      console.log('moment-lingo-extension 插件登录成功');
    }
  });
})();

function handleTextSelection() {
  // 检查是否登录以及划词翻译开关是否开启
  try {
    if (!chrome || !chrome.storage || !chrome.storage.local) {
      console.warn('插件上下文已失效，请刷新页面后重试划词翻译功能。');
      return;
    }

    chrome.storage.local.get(['userStore', 'wordSelectionEnabled'], result => {
      // 未登录或者划词翻译开关未开启（默认为 true，所以只有明确为 false 时才不处理）
      if (!result.userStore || result.wordSelectionEnabled === false) {
        return;
      }

      // 如果翻译弹窗正在显示，则不显示选项弹窗
      if (isTranslationPopupVisible) {
        return;
      }

      const selectedText = window.getSelection().toString().trim();

      if (selectedText.length > 0 && selectedText.length <= 1000) {
        showOptionsPopup(selectedText);
      } else if (selectedText.length > 1000) {
        hideOptionsPopup();
      } else {
        hideOptionsPopup();
      }
    });
  } catch (e) {
    console.warn('Cannot read extension storage. Extension might be reloaded or context invalidated.', e);
  }
}

function showOptionsPopup(text) {
  hideOptionsPopup();

  const popup = document.createElement('div');
  popup.id = 'moment-lingo-options-popup';
  popup.className = 'moment-lingo-options-popup';

  popup.innerHTML = `
        <button class="option-btn copy-btn" data-action="copy" title="复制">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M13 1H3C1.89543 1 1 1.89543 1 3V11" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <rect x="3" y="5" width="10" height="10" rx="2" stroke="currentColor" stroke-width="2"/>
          </svg>
        </button>
        <button class="option-btn translate-btn" data-action="translate" title="翻译">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M2 2L14 14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <path d="M2 14L14 2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <circle cx="8" cy="8" r="7" stroke="currentColor" stroke-width="2"/>
            <path d="M5 8H11" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <path d="M8 5V11" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>
    `;

  document.body.appendChild(popup);
  positionPopup(popup);

  setTimeout(() => {
    popup.classList.add('show');
  }, 10);

  popup.querySelector('.copy-btn').addEventListener('click', function (e) {
    e.stopPropagation();
    copyTextToClipboard(text);
    hideOptionsPopup();
  });

  popup.querySelector('.translate-btn').addEventListener('click', function (e) {
    e.stopPropagation();
    hideOptionsPopup();
    showTranslationPopup(text);
  });

  const closeListener = function (e) {
    if (!popup.contains(e.target) && e.target !== popup) {
      hideOptionsPopup();
      document.removeEventListener('click', closeListener);
    }
  };

  setTimeout(() => {
    document.addEventListener('click', closeListener);
  }, 100);
}

function hideOptionsPopup() {
  const existingPopup = document.getElementById('moment-lingo-options-popup');
  if (existingPopup) {
    // 添加退出动画
    existingPopup.classList.remove('show');
    setTimeout(() => {
      if (existingPopup.parentNode) {
        existingPopup.remove();
      }
    }, 200);
  }
}

function positionPopup(popup) {
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
  const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;

  let top = mousePosition.y + scrollTop + 5;
  let left = mousePosition.x + scrollLeft + 5;

  const popupRect = popup.getBoundingClientRect();

  if (top + popupRect.height > window.innerHeight + scrollTop) {
    top = mousePosition.y + scrollTop - popupRect.height - 5;
  }

  if (left + popupRect.width > window.innerWidth + scrollLeft) {
    left = mousePosition.x + scrollLeft - popupRect.width - 5;
  }

  if (left < scrollLeft + 5) {
    left = scrollLeft + 5;
  }

  if (top < scrollTop + 5) {
    top = scrollTop + 5;
  }

  popup.style.top = top + 'px';
  popup.style.left = left + 'px';
}

// 复制文本到剪贴板
function copyTextToClipboard(text) {
  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(text).then(() => {
      showNotification('文本已复制到剪贴板');
    }).catch(err => {
      console.error('复制失败:', err);
      fallbackCopyTextToClipboard(text);
    });
  } else {
    // 兼容性处理
    fallbackCopyTextToClipboard(text);
  }
}

function fallbackCopyTextToClipboard(text) {
  const textArea = document.createElement('textarea');
  textArea.value = text;

  // 避免滚动到底部
  textArea.style.top = '0';
  textArea.style.left = '0';
  textArea.style.position = 'fixed';
  textArea.style.opacity = '0';

  document.body.appendChild(textArea);
  textArea.focus();
  textArea.select();

  try {
    const successful = document.execCommand('copy');
    if (successful) {
      showNotification('文本已复制到剪贴板');
    } else {
      console.error('复制命令失败');
    }
  } catch (err) {
    console.error('复制命令出错:', err);
  }

  document.body.removeChild(textArea);
}

// 显示通知
function showNotification(message) {
  // 移除已存在的通知
  const existingNotification = document.getElementById('moment-lingo-notification');
  if (existingNotification) {
    // 添加淡出效果
    existingNotification.classList.add('hide');
    setTimeout(() => {
      if (existingNotification.parentNode) {
        existingNotification.remove();
      }
    }, 300);
  }

  // 创建通知元素
  const notification = document.createElement('div');
  notification.id = 'moment-lingo-notification';
  notification.className = 'moment-lingo-notification';
  notification.textContent = message;

  // 添加到页面中
  document.body.appendChild(notification);

  // 触发进入动画
  setTimeout(() => {
    notification.classList.add('show');
  }, 10);

  // 3秒后自动移除
  setTimeout(() => {
    if (notification.parentNode) {
      notification.classList.add('hide');
      setTimeout(() => {
        if (notification.parentNode) {
          notification.remove();
        }
      }, 300);
    }
  }, 3000);
}

// 翻译弹窗
function showTranslationPopup(text) {
  // 移除已存在的弹窗
  hideTranslationPopup();

  // 隐藏选项弹窗
  hideOptionsPopup();

  // 设置翻译弹窗可见标志
  isTranslationPopupVisible = true;

  // 创建新的弹窗元素
  const popup = document.createElement('div');
  popup.id = 'moment-lingo-translation-popup';
  popup.className = 'moment-lingo-translation-popup';

  // 设置弹窗内容
  popup.innerHTML = `
        <div class="popup-header">
            <span class="popup-title">翻译结果</span>
            <button class="close-btn">&times;</button>
        </div>
        <div class="popup-content">
            <div class="original-text">${escapeHtml(text)}</div>
            <div class="translation-result loading">翻译中...</div>
        </div>
    `;

  // 添加到页面中
  document.body.appendChild(popup);

  // 定位弹窗在选中文本附近
  positionTranslationPopup(popup);

  // 触发进入动画
  setTimeout(() => {
    popup.classList.add('show');
  }, 10);

  // 绑定关闭事件
  popup.querySelector('.close-btn').addEventListener('click', function (e) {
    e.stopPropagation();
    hideTranslationPopup();
  });

  // 添加拖拽功能
  const popupHeader = popup.querySelector('.popup-header');
  let isDragging = false;
  let currentX;
  let currentY;
  let initialX;
  let initialY;
  let xOffset = 0;
  let yOffset = 0;

  // 鼠标按下事件
  popupHeader.addEventListener('mousedown', dragStart);

  // 鼠标移动事件
  document.addEventListener('mousemove', drag);

  // 鼠标释放事件
  document.addEventListener('mouseup', dragEnd);

  function dragStart(e) {
    // 只有在标题栏上按下鼠标左键才开始拖拽
    if (e.target === popupHeader || popupHeader.contains(e.target)) {
      initialX = e.clientX - xOffset;
      initialY = e.clientY - yOffset;

      isDragging = true;
      popup.style.cursor = 'move';
      popup.style.userSelect = 'none';
    }
  }

  function drag(e) {
    if (isDragging) {
      e.preventDefault();

      currentX = e.clientX - initialX;
      currentY = e.clientY - initialY;

      xOffset = currentX;
      yOffset = currentY;

      setTranslate(currentX, currentY, popup);
    }
  }

  function dragEnd() {
    initialX = currentX;
    initialY = currentY;

    isDragging = false;
    popup.style.cursor = 'default';
    popup.style.userSelect = 'auto';
  }

  function setTranslate(xPos, yPos, el) {
    el.style.transform = `translate3d(${xPos}px, ${yPos}px, 0)`;
  }

  // 点击弹窗外关闭
  const closeListener = function (e) {
    if (!popup.contains(e.target) && e.target !== popup) {
      hideTranslationPopup();
      document.removeEventListener('click', closeListener);
    }
  };

  // 延迟添加监听器，避免立即触发
  setTimeout(() => {
    document.addEventListener('click', closeListener);
  }, 100);

  // 执行翻译
  performTranslation(text, popup);
}

function hideTranslationPopup() {
  const existingPopup = document.getElementById('moment-lingo-translation-popup');
  if (existingPopup) {
    // 添加退出动画
    existingPopup.classList.remove('show');
    setTimeout(() => {
      if (existingPopup.parentNode) {
        existingPopup.remove();
      }
    }, 300);
  }

  // 设置翻译弹窗不可见标志
  isTranslationPopupVisible = false;
}

function positionTranslationPopup(popup) {
  // 使用鼠标位置而不是选中文本位置
  const scrollTop = window.pageYOffset ?? document.documentElement.scrollTop;
  const scrollLeft = window.pageXOffset ?? document.documentElement.scrollLeft;

  // 默认放在鼠标位置附近
  let top = mousePosition.y + scrollTop - popup.offsetHeight - 10;
  let left = mousePosition.x + scrollLeft;

  // 确保弹窗不会超出视窗边界
  // 如果上方空间不足，放在下方
  if (top < scrollTop + 10) {
    top = mousePosition.y + scrollTop + 10;
  }

  // 如果右方超出边界，则调整位置
  const maxLeft = window.innerWidth + scrollLeft - popup.offsetWidth - 10;
  if (left > maxLeft) {
    left = maxLeft;
  }

  // 确保左侧不会小于0
  if (left < scrollLeft + 10) {
    left = scrollLeft + 10;
  }

  popup.style.top = top + 'px';
  popup.style.left = left + 'px';
}


function performTranslation(text, popup) {
  const translationResult = popup.querySelector('.translation-result');
  if (translationResult) {
    translationResult.classList.add('loading');
    translationResult.textContent = '翻译中...';
    let currentTranslation = '';

    translate(
      text,
      (content) => { // onProgress
        translationResult.classList.remove('loading');

        if (typeof content === 'object' && content !== null) {
          // 如果后端直接返回的是对象，直接进行结构化展示
          const data = content;
          let translationsHtml = '';
          if (Array.isArray(data.translation)) {
            translationsHtml = data.translation.map(t => `<span class="dict-trans-item">${escapeHtml(t)}</span>`).join('');
          }

          translationResult.innerHTML = `
            <div class="dict-result">
              ${data.word ? `<div class="dict-word">${escapeHtml(data.word)}</div>` : ''}
              <div class="dict-translations">
                ${translationsHtml}
              </div>
              ${data.url ? `<a href="${escapeHtml(data.url)}" target="_blank" class="dict-link">查看详情 &rarr;</a>` : ''}
            </div>
          `;
        } else {
          // 如果是普通文本（流式或一次性字符串），作为文本追加
          currentTranslation += (content || '');
          translationResult.textContent = currentTranslation;
        }
      },
      () => { // onComplete
        translationResult.classList.remove('loading');
      },
      (err) => { // onError
        console.error('翻译出错:', err);
        translationResult.classList.remove('loading');
        translationResult.textContent = err.message || '翻译失败，请检查网络连接';
      }
    );
  }
}

function escapeHtml(text) {
  const map = {
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', '\'': '&#039;'
  };

  return text.replace(/[&<>"']/g, function (m) {
    return map[m];
  });
}


function translate(text, onProgress, onComplete, onError) {
  chrome.storage.local.get('userStore', async store => {
    try {
      const userStore = JSON.parse(store.userStore ?? '{}');
      const token = userStore.refUserInfo?.token ?? '';

      const response = await fetch('https://www.momentlingo.cn/api/ai/extension/translate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({content: text})
      });

      const contentType = response.headers.get('Content-Type');
      if (!contentType || !contentType.includes('text/event-stream')) {
        const resJson = await response.json();
        if (resJson.code !== 200) {
          throw new Error(resJson.msg || '请求异常');
        }
        return;
      }

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }


      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';
      let currentEvent = '';

      while (true) {
        const {done, value} = await reader.read();
        if (done) {
          break;
        }

        buffer += decoder.decode(value, {stream: true});
        const lines = buffer.split('\n');

        buffer = lines.pop() || ''; // Keep the incomplete line in buffer

        for (const line of lines) {
          if (line.trim() === '') {
            // 空行代表一个完整的事件块结束，但如果是我们自己维护逻辑，可以在这里做一些清理工作
            continue;
          }

          if (line.startsWith('event:')) {
            currentEvent = line.slice(6).trim();
          } else if (line.startsWith('data:')) {
            const dataStr = line.slice(5).trim();

            try {
              const data = JSON.parse(dataStr);

              if (currentEvent === 'PROCESSING' && data.content) {
                onProgress(data.content);
              } else if (currentEvent === 'END') {
                onComplete();
                return;
              } else if (currentEvent === 'ERROR') {
                throw new  Error(data.content || 'Translation error');
              }
            } catch (e) {
              console.error('Error parsing SSE message:', e, line);
            }
          }
        }
      }
    } catch (err) {
      onError(err);
    }
  });
}