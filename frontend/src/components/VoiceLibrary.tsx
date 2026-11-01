'use client';

import React, { useRef, useState } from 'react';
import {
  ArrowRight,
  CheckCircle,
  Mic,
  Pause,
  Play,
  Sparkles,
  User,
  Volume2,
} from 'lucide-react';
import { VoiceMetadata } from '@/types/tts';
import { getSpeakerPreviewUrl } from '@/services/api';

interface VoiceLibraryProps {
  voices: VoiceMetadata[];
  onSelectAndUse: (voiceId: string) => void;
}

export const VoiceLibrary: React.FC<VoiceLibraryProps> = ({
  voices,
  onSelectAndUse,
}) => {
  const [playingVoiceId, setPlayingVoiceId] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [filterGender, setFilterGender] = useState<'all' | 'male' | 'female'>('all');

  const filteredVoices = voices.filter((v) => {
    if (filterGender === 'all') return true;
    return v.gender === filterGender;
  });

  const togglePreview = (voiceId: string) => {
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
        console.warn('Playback error:', err);
        setPlayingVoiceId(null);
      });

      audio.onended = () => setPlayingVoiceId(null);
      audio.onerror = () => setPlayingVoiceId(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & Filter Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 rounded-2xl border border-white/[0.08] bg-[#0E1320]/80 p-6 backdrop-blur-xl">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Mic className="h-5 w-5 text-primary-400" />
            <span>Hindi Voice Library (आवाज़ पुस्तकालय)</span>
          </h2>
          <p className="mt-1 text-sm text-slate-400 font-devanagari">
            Indic Parler-TTS मॉडल पर आधारित वास्तविक और प्रामाणिक भारतीय स्वर शैलियाँ।
          </p>
        </div>

        {/* Gender Filter Buttons */}
        <div className="flex items-center space-x-1.5 rounded-xl bg-[#090C14] p-1 border border-white/[0.04]">
          <button
            type="button"
            onClick={() => setFilterGender('all')}
            className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition ${
              filterGender === 'all'
                ? 'bg-primary-600 text-white shadow'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            All Voices ({voices.length})
          </button>
          <button
            type="button"
            onClick={() => setFilterGender('female')}
            className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition ${
              filterGender === 'female'
                ? 'bg-pink-600 text-white shadow'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Female (महिला)
          </button>
          <button
            type="button"
            onClick={() => setFilterGender('male')}
            className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition ${
              filterGender === 'male'
                ? 'bg-indigo-600 text-white shadow'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Male (पुरुष)
          </button>
        </div>
      </div>

      {/* Voice Detailed Cards */}
      <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
        {filteredVoices.map((voice) => {
          const isPlaying = playingVoiceId === voice.id;

          return (
            <div
              key={voice.id}
              className="flex flex-col justify-between rounded-2xl border border-white/[0.08] bg-[#0E1320]/90 p-6 shadow-xl backdrop-blur-xl transition hover:border-white/[0.15] hover:bg-[#111726]"
            >
              <div>
                {/* Header */}
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3.5">
                    <div
                      className={`flex h-12 w-12 items-center justify-center rounded-2xl font-bold shadow-lg ${
                        voice.gender === 'female'
                          ? 'bg-gradient-to-tr from-pink-500 to-rose-600 text-white'
                          : 'bg-gradient-to-tr from-indigo-500 to-primary-700 text-white'
                      }`}
                    >
                      <User className="h-6 w-6" />
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-white font-devanagari flex items-center gap-2">
                        {voice.name}
                        {voice.recommended && (
                          <span className="inline-flex items-center rounded-md bg-amber-500/15 px-2 py-0.5 text-[10px] font-semibold text-amber-400 border border-amber-500/30">
                            Recommended
                          </span>
                        )}
                      </h3>
                      <div className="flex items-center space-x-2 text-xs text-slate-400">
                        <span className="capitalize font-medium text-slate-300">
                          {voice.gender === 'female' ? 'महिला (Female)' : 'पुरुष (Male)'}
                        </span>
                        <span>•</span>
                        <span>Official Hindi Speaker</span>
                      </div>
                    </div>
                  </div>

                  {/* Audio Preview Button */}
                  <button
                    type="button"
                    onClick={() => togglePreview(voice.id)}
                    className={`flex h-10 w-10 items-center justify-center rounded-xl transition ${
                      isPlaying
                        ? 'bg-primary-500 text-white animate-pulse shadow-lg shadow-primary-500/30'
                        : 'bg-white/[0.05] text-slate-300 hover:bg-white/[0.1] hover:text-white'
                    }`}
                    title={isPlaying ? 'Pause sample' : 'Listen to voice sample'}
                  >
                    {isPlaying ? (
                      <Pause className="h-4 w-4 fill-current" />
                    ) : (
                      <Play className="h-4 w-4 fill-current translate-x-0.5" />
                    )}
                  </button>
                </div>

                {/* Description */}
                <p className="mt-4 text-sm text-slate-300 leading-relaxed font-devanagari">
                  {voice.description}
                </p>

                {/* Sample Sentence Quote Box */}
                <div className="mt-3.5 rounded-xl bg-black/40 p-3.5 border border-white/[0.04]">
                  <span className="text-[11px] font-semibold text-slate-400 block mb-1">
                    नमूना वाक्य (Sample Sentence):
                  </span>
                  <p className="text-xs text-primary-200/90 italic font-devanagari">
                    &ldquo;{voice.sample_text}&rdquo;
                  </p>
                </div>

                {/* Supported Styles Tags */}
                <div className="mt-4">
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block mb-1.5">
                    Supported Styles (शैलियाँ):
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {voice.supported_styles.map((st) => (
                      <span
                        key={st}
                        className="rounded-md bg-white/[0.04] px-2 py-0.5 text-[11px] font-medium text-slate-300 border border-white/[0.04] capitalize"
                      >
                        {st}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Action Button: Use this voice */}
              <div className="mt-6 pt-4 border-t border-white/[0.06]">
                <button
                  type="button"
                  onClick={() => onSelectAndUse(voice.id)}
                  className="flex w-full items-center justify-center space-x-2 rounded-xl bg-white/[0.04] py-2.5 text-xs font-bold text-slate-200 transition hover:bg-primary-600 hover:text-white group border border-white/[0.06]"
                >
                  <span>Use {voice.name.split(' ')[0]} to Generate Speech</span>
                  <ArrowRight className="h-3.5 w-3.5 transition group-hover:translate-x-1" />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
