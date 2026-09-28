import { useMSEAudioPlayer } from './useMSEAudioPlayer';
import { useACAudioPlayer } from './useACAudioPlayer';
import type { AudioPlayer, AudioPlayerInstance, AudioPlayerOptions } from 'src/composables/types.ts';

class AudioPlayerFactory {
  static create(): AudioPlayer {
    const isMseSupported = window.MediaSource && MediaSource.isTypeSupported('audio/mpeg');
    if (isMseSupported) {
      console.log('MediaSource支持audio/mpeg，将使用MSEAudioPlayer');
      return new useMSEAudioPlayer();
    } else {
      console.log('MediaSource不支持audio/mpeg，将使用AudioContext降级方案');
      return new useACAudioPlayer();
    }
  }
}


export { AudioPlayerFactory };
export type { AudioPlayerOptions, AudioPlayerInstance, AudioPlayer };
