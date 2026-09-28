declare module 'vue-cropper' {
  import type { DefineComponent } from 'vue';
  export const VueCropper: DefineComponent<{}, {}, any>;
  export default VueCropper;
}

declare module 'vue-cropper/lib/vue-cropper.vue' {
  import type { DefineComponent } from 'vue';
  const component: DefineComponent<{}, {}, any>;
  export default component;
}
