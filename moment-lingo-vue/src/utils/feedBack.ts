import { Message, Notification } from '@arco-design/web-vue';
import { useMobileDetector } from '@/utils/mobileDetector.ts';
import { Message as TMessage } from 'tdesign-mobile-vue';

const { isMobile } = useMobileDetector();

const MlMessage = {
  info: (msg: string) => messageInfo(msg),
  success: (msg: string) => messageSuccess(msg),
  warning: (msg: string) => messageWarning(msg),
  error: (msg: string) => messageError(msg)
};


const MlNotification = {
  info: (title: string, content: string) => notificationInfo(title, content),
  success: (title: string, content: string) => notificationSuccess(title, content),
  warning: (title: string, content: string) => notificationWarning(title, content),
  error: (title: string, content: string) => notificationError(title, content)
};

function messageInfo(msg: string) {
  if (isMobile.value) {
    TMessage.info({
      offset: [10, 16],
      content: msg,
      single: false
    });
  } else {
    Message.info(msg);
  }
}

function messageSuccess(msg: string) {
  if (isMobile.value) {
    TMessage.success({
      offset: [10, 16],
      content: msg,
      single: false
    });
  } else {
    Message.success(msg);
  }
}

function messageWarning(msg: string) {
  if (isMobile.value) {
    TMessage.warning({
      offset: [10, 16],
      content: msg,
      single: false
    });
  } else {
    Message.warning(msg);
  }
}

function messageError(msg: string) {
  if (isMobile.value) {
    TMessage.error({
      offset: [10, 16],
      content: msg,
      single: false
    });
  } else {
    Message.error(msg);
  }
}

function notificationInfo(title: string, content: string) {
  if (!isMobile.value) {
    Notification.info({
      title,
      content
    });
  }
}


function notificationWarning(title: string, content: string) {
  if (!isMobile.value) {
    Notification.warning({
      title,
      content
    });
  }
}


function notificationError(title: string, content: string) {
  if (!isMobile.value) {
    Notification.error({
      title,
      content
    });
  }
}

function notificationSuccess(title: string, content: string) {
  if (!isMobile.value) {
    Notification.success({
      title,
      content
    });
  }
}

export {
  MlMessage,
  MlNotification
};

