import type { Ref } from 'vue';

export interface AudioPlayerOptions {
  content: string;
  model: string;
  voiceKey: string;
}

export interface AudioPlayerInstance {
  tts: () => void;
  onPlay: () => void;
  onPause: () => void;
  onToggle: (toStart?: boolean) => void;
  destroy: () => void;
  isPlaying: Ref<boolean>;
  isLoading: Ref<boolean>;
  isAllLoaded: Ref<boolean>;
}

export interface AudioPlayer {
  readonly isLoading: boolean;
  readonly isPlaying: boolean;
  readonly isAllLoaded: boolean;
  setOptions: (options: AudioPlayerOptions) => void;
  play: () => void;
  pause: () => void;
  toggle: (toStart?: boolean) => void;
}
