import { createVNode, markRaw, type Ref, ref, render, watch } from 'vue';
import MlMseAudioPlayer from '../components/audio/MlMSEAudioPlayer.vue';
import type { AudioPlayerOptions, AudioPlayerInstance, AudioPlayer } from './types';

function createAudioPlayer(options: AudioPlayerOptions): AudioPlayerInstance {
  // 创建挂载容器
  const container = document.body;
  const wrapper = document.createElement('div');
  container.appendChild(wrapper);

  // 创建组件实例
  const app = createVNode(MlMseAudioPlayer, {
    content: options.content,
    model: options.model,
    voiceKey: options.voiceKey
  });

  // 渲染组件
  render(app, wrapper);

  // 获取组件暴露的方法
  const exposed = app.component?.exposed as any;

  // 返回的实例对象
  return {
    tts: () => exposed?.tts?.(),
    onPlay: () => exposed?.onPlay?.(),
    onPause: () => exposed?.onPause?.(),
    onToggle: (toStart?: boolean) => exposed?.onToggle?.(toStart),
    destroy: () => {
      // 销毁组件并移除DOM
      render(null, wrapper);
      if (wrapper.parentNode) {
        wrapper.parentNode.removeChild(wrapper);
      }
    },
    isLoading: exposed?.isLoading as Ref<boolean>,
    isPlaying: exposed?.isPlaying as Ref<boolean>,
    isAllLoaded: exposed?.isAllLoaded as Ref<boolean>
  };
}

class useMSEAudioPlayer implements AudioPlayer {
  private options: AudioPlayerOptions | null;
  private player: AudioPlayerInstance | null;
  private readonly _isLoading: Ref<boolean>;
  private readonly _isPlaying: Ref<boolean>;
  private readonly _isAllLoaded: Ref<boolean>;

  constructor() {
    markRaw(this);
    this.options = null;
    this.player = null;
    this._isLoading = ref(false);
    this._isPlaying = ref(false);
    this._isAllLoaded = ref(false);
  }

  get isLoading() {
    return this._isLoading.value;
  }

  get isPlaying() {
    return this._isPlaying.value;
  }

  get isAllLoaded() {
    return this._isAllLoaded.value;
  }

  setOptions(options: AudioPlayerOptions) {
    if (this.options === null) {
      this.createNewPlayer(options);
    }

    if (this.options?.model !== options.model || this.options?.voiceKey !== options.voiceKey) {
      this.createNewPlayer(options);
    }
  }

  play() {
    this.player?.onPlay();
  }

  pause() {
    this.player?.onPause();
  }

  toggle(toStart: boolean = false) {
    this.player?.onToggle(toStart);
  }

  private watchRef() {
    // 监听原始的 isLoading 和 isPlaying 状态变化并同步到响应式引用
    if (this.player?.isLoading) {
      watch(this.player.isLoading, (newValue) => {
        this._isLoading.value = newValue;
      });
    }

    if (this.player?.isPlaying) {
      watch(this.player.isPlaying, (newValue) => {
        this._isPlaying.value = newValue;
      });
    }

    if (this.player?.isAllLoaded) {
      watch(this.player.isAllLoaded, (newValue) => {
        this._isAllLoaded.value = newValue;
      });
    }
  }

  private createNewPlayer(options: AudioPlayerOptions) {
    this.player?.destroy();

    this.options = options;
    this.player = createAudioPlayer(options);
    this.watchRef();
    this.player.tts();
  }
}

export { useMSEAudioPlayer };

