const loginBtn = document.getElementById('loginBtn');
const logoutBtn = document.getElementById('logoutBtn');
const wordSelectionToggle = document.getElementById('wordSelectionToggle');
const userInfo = document.getElementById('userInfo');
const userAvatar = document.getElementById('userAvatar');
const userNickname = document.getElementById('userNickname');
const settingsSection = document.getElementById('settingsSection');

// 初始化
document.addEventListener('DOMContentLoaded', () => {
  loadSettings();
  bindEventListeners();
});

// 加载设置
function loadSettings() {
  chrome.storage.local.get(['wordSelectionEnabled'], (result) => {
    // 默认为 true，只有明确保存为 false 时才关闭
    wordSelectionToggle.checked = result.wordSelectionEnabled !== false;
  });
}

function bindEventListeners() {
  // 登录/登出按钮
  loginBtn.addEventListener('click', handleLogin);
  if (logoutBtn) {
    logoutBtn.addEventListener('click', handleLogout);
  }

  // 功能开关
  wordSelectionToggle.addEventListener('change', handleWordSelectionToggle);

  // 检查认证状态
  checkAuthStatus();
}


function handleLogin() {
  window.open('https://momentlingo.cn/auth', '_blank');
}

// 划词翻译开关处理
function handleWordSelectionToggle() {
  const isEnabled = wordSelectionToggle.checked;
  chrome.storage.local.set({wordSelectionEnabled: isEnabled});
}

// 检查认证状态
function checkAuthStatus() {
  chrome.storage.local.get('userStore', (result) => {
    if (!result.userStore) {
      showLoginButton();
      return;
    }
    try {
      const userStore = JSON.parse(result.userStore);
      showUserInfo(userStore);
    } catch (e) {
      console.error('Failed to parse userStore:', e);
      showLoginButton();
    }
  });
}

// 显示用户信息
function showUserInfo(userStore) {
  if (userStore && userStore.refUserInfo) {
    const {avatarUrl, nickname} = userStore.refUserInfo;
    // 设置用户头像
    if (userAvatar) {
      userAvatar.src = avatarUrl || '/public/logo.png';
    }

    // 设置用户昵称
    if (userNickname) {
      userNickname.textContent = nickname || '用户';
    }

    // 显示用户信息区域
    if (userInfo) {
      userInfo.style.display = 'flex';
    }

    // 隐藏登录按钮
    if (loginBtn) {
      loginBtn.style.display = 'none';
    }

    // 显示设置区域
    if (settingsSection) {
      settingsSection.style.display = 'block';
    }
  } else {
    showLoginButton();
  }
}


// 显示登录按钮
function showLoginButton() {
  if (userInfo) {
    userInfo.style.display = 'none';
  }
  if (loginBtn) {
    loginBtn.style.display = 'flex';
  }
  // 隐藏设置区域
  if (settingsSection) {
    settingsSection.style.display = 'none';
  }
}

// 登出处理
function handleLogout() {
  chrome.storage.local.remove('userStore', () => {
    // 清除成功后，显示登录按钮
    showLoginButton();
  });
}