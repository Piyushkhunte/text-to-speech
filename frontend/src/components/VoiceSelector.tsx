'use client';

import React, { useRef, useState } from 'react';
import {
  Check,
  Pause,
  Play,
  Sparkles,
  User,
  Volume2,
} from 'lucide-react';
import { VoiceMetadata } from '@/types/tts';
import { getSpeakerPreviewUrl } from '@/services/api';

interface VoiceSelectorProps {
  voices: VoiceMetadata[];
  selectedVoiceId: string;
  onSelectVoice: (id: string) => void;
  disabled?: boolean;
}

export const VoiceSelector: React.FC<VoiceSelectorProps> = ({
  voices,
  selectedVoiceId,
  onSelectVoice,
  disabled = false,
}) => {
  const [playingVoiceId, setPlayingVoiceId] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const handleTogglePreview = (e: React.MouseEvent, voiceId: string) => {
    e.stopPropagation();

    if (playingVoiceId === voiceId) {
      audioRef.current?.pause();
      setPlayingVoiceId(null);
    } else {
      if (audioRef.current) {
        audioRef.current.pause();
      }
      const previewUrl = getSpeakerPreviewUrl(voiceId);
      const audio = new Audio(previewUrl);
      audioRef.current = audio;
      setPlayingVoiceId(voiceId);

      audio.play().catch((err) => {
        console.warn('Audio preview play error:', err);
        setPlayingVoiceId(null);
      });

      audio.onended = () => {
        setPlayingVoiceId(null);
      };
      audio.onerror = () => {
        setPlayingVoiceId(null);
      };
    }
  };

  return (
    <div className="rounded-2xl border border-white/[0.08] bg-[#0E1320]/80 p-5 shadow-2xl backdrop-blur-xl">
      <div className="flex items-center justify-between border-b border-white/[0.06] pb-3 mb-4">
        <div className="flex items-center space-x-2">
          <span className="flex h-2.5 w-2.5 rounded-full bg-accent-purple" />
          <h2 className="text-sm font-semibold text-white tracking-wide uppercase">
            Select Hindi Voice (आवाज़ चयन)
          </h2>
        </div>
        <span className="text-xs text-slate-400">
          {voices.length} Verified Speakers Available
        </span>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {voices.map((voice) => {
          const isSelected = selectedVoiceId === voice.id;
          const isPlaying = playingVoiceId === voice.id;

          return (
            <div
              key={voice.id}
              onClick={() => !disabled && onSelectVoice(voice.id)}
              className={`group relative flex flex-col justify-between rounded-xl p-4 transition cursor-pointer border ${
                isSelected
                  ? 'border-primary-500 bg-primary-600/10 shadow-lg shadow-primary-500/15 ring-1 ring-primary-500'
                  : 'border-white/[0.06] bg-[#0B0E17] hover:border-white/[0.15] hover:bg-[#0E1322]'
              } ${disabled ? 'cursor-not-allowed opacity-50' : ''}`}
            >
              {/* Card Header: Avatar & Badges */}
              <div>
                <div className="flex items-start justify-between">
                  <div
                    className={`flex h-11 w-11 items-center justify-center rounded-xl font-bold shadow-md ${
                      voice.gender === 'female'
                        ? 'bg-gradient-to-br from-pink-500 to-rose-600 text-white'
                        : 'bg-gradient-to-br from-indigo-500 to-primary-700 text-white'
                    }`}
                  >
                    <User className="h-5 w-5" />
                  </div>

                  <div className="flex items-center space-x-1">
                    {voice.recommended && (
                      <span className="inline-flex items-center rounded-md bg-amber-500/15 px-2 py-0.5 text-[10px] font-semibold text-amber-400 border border-amber-500/30">
                        <Sparkles className="mr-1 h-2.5 w-2.5" /> Recommended
                      </span>
                    )}

                    {isSelected && (
                      <div className="flex h-5 w-5 items-center justify-center rounded-full bg-primary-500 text-white">
                        <Check className="h-3 w-3 stroke-[3]" />
                      </div>
                    )}
                  </div>
                </div>

                {/* Voice Name & Gender */}
                <div className="mt-3">
                  <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-1.5 font-devanagari">
                    {voice.name}
                  </h3>
                  <div className="mt-0.5 flex items-center space-x-2 text-xs text-slate-400 capitalize">
                    <span className="rounded bg-white/[0.05] px-1.5 py-0.5 font-medium text-slate-300">
                      {voice.gender === 'female' ? 'महिला (Female)' : 'पुरुष (Male)'}
                    </span>
                    <span>•</span>
                    <span>Hindi Native</span>
                  </div>
                </div>

                {/* Description */}
                <p className="mt-2 text-xs text-slate-400 leading-relaxed line-clamp-2 font-devanagari">
                  {voice.description}
                </p>
              </div>

              {/* Card Footer: Preview Play Button */}
              <div className="mt-4 pt-3 border-t border-white/[0.04] flex items-center justify-between">
                <button
                  type="button"
                  onClick={(e) => handleTogglePreview(e, voice.id)}
                  className={`flex items-center space-x-1.5 rounded-lg px-2.5 py-1 text-xs font-medium transition ${
                    isPlaying
                      ? 'bg-primary-500 text-white animate-pulse'
                      : 'bg-white/[0.04] text-slate-300 hover:bg-white/[0.08] hover:text-white'
                  }`}
                >
                  {isPlaying ? (
                    <>
                      <Pause className="h-3 w-3 fill-current" />
                      <span>Pause</span>
                    </>
                  ) : (
                    <>
                      <Play className="h-3 w-3 fill-current" />
                      <span>Preview</span>
                    </>
                  )}
                </button>

                <span className="text-[11px] text-slate-500">
                  {voice.id === 'rohit' ? 'Conversational' : voice.id === 'divya' ? 'Expressive' : voice.id === 'aman' ? 'Deep' : 'Melodious'}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
