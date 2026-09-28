import { createRouter, createWebHistory } from 'vue-router';
import NProgress from 'nprogress';
import 'nprogress/nprogress.css';
import { useMobileDetector } from '@/utils/mobileDetector.ts';
import { useUserStore } from '@/store/userStore.ts';

const routes = [
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFoundView.vue')
  },
  {
    path: '/',
    name: 'Index',
    meta: { transition: 'fade-from-bottom' },
    component: () => import('@/views/IndexView.vue')
  },
  {
    path: '/vocabulary/:vocabularyId',
    name: 'Vocabulary',
    component: () => import('@/views/vocabulary/VocabularyLayoutView.vue')
  },
  {
    path: '/search',
    name: 'Search',
    component: () => import('@/views/SearchView.vue')
  },
  {
    path: '/auth',
    name: 'Auth',
    redirect: '/auth/login',
    children: [
      {
        path: 'login',
        name: 'LoginView',
        component: () => import('@/views/auth/LoginView.vue')
      },
      {
        path: 'register',
        name: 'Register',
        component: () => import('@/views/auth/RegisterView.vue')
      }
    ],
  },
  {
    path: '/essay',
    name: 'Essay',
    redirect: '/essay/correct',
    meta: { auth: true },
    component: () => import('@/views/essay/EssayLayoutView.vue'),
    children: [
      {
        path: 'correct',
        name: 'EssayCorrect',
        component: () => import('@/views/essay/EssayCorrectView.vue')
      },
      {
        path: 'correct/:id',
        name: 'EssayCorrectDetail',
        component: () => import('@/views/essay/EssayCorrectDetailView.vue')
      }
    ]
  },
  {
    path: '/h5-upload',
    name: 'H5Upload',
    component: () => import('@/views/H5UploadView.vue')
  },
  {
    path: '/ai-call',
    name: 'AiCall',
    meta: { auth: true },
    component: () => import('../views/AICallView.vue')
  },
  {
    path: '/book',
    name: 'Book',
    redirect: '/book/list',
    meta: { auth: true },
    component: () => import('@/views/book/BookLayoutView.vue'),
    children: [
      {
        path: 'list',
        name: 'BookList',
        component: () => import('@/views/book/BookListView.vue')
      },
      {
        path: ':bookId',
        name: 'BookDetail',
        component: () => import('@/views/book/BookDetailView.vue')
      }
    ]
  },
  {
    path: '/user',
    name: 'User',
    meta: { auth: true },
    component: () => import('@/views/UserView.vue'),
  },
  {
    path: '/ai-write',
    name: 'AIWrite',
    meta: { auth: true },
    component: () => import('@/views/AIWriteView.vue')
  }
];

const router = createRouter({
  // 打包使用
  // history: createWebHashHistory(),
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 };
  }
});

const { isMobile } = useMobileDetector();
NProgress.configure({
  showSpinner: false
});

router.beforeEach((to: any, __, next) => {
  const userStore = useUserStore();
  if (!isMobile.value) {
    NProgress.start();
  }

  if (to.meta.auth === true && !userStore.isLogin()) {
    console.log('未登录，跳转登录页');
    next({
      path: '/auth'
    });
    return;
  }

  next();
});

router.afterEach(() => {
  if (!isMobile.value) {
    NProgress.done();
  }
});


export default router;