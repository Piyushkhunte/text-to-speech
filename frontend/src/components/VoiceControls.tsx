'use client';

import React from 'react';
import {
  Activity,
  Gauge,
  Sliders,
  Sparkles,
  Volume2,
  Wand2,
} from 'lucide-react';
import { AudioFormat, PitchLevel, SpeakingStyle } from '@/types/tts';

interface VoiceControlsProps {
  speed: number;
  setSpeed: (val: number) => void;
  pitch: PitchLevel;
  setPitch: (val: PitchLevel) => void;
  style: SpeakingStyle;
  setStyle: (val: SpeakingStyle) => void;
  audioFormat: AudioFormat;
  setAudioFormat: (val: AudioFormat) => void;
  onGenerate: () => void;
  isGenerating: boolean;
  disabled?: boolean;
}

export const VoiceControls: React.FC<VoiceControlsProps> = ({
  speed,
  setSpeed,
  pitch,
  setPitch,
  style,
  setStyle,
  audioFormat,
  setAudioFormat,
  onGenerate,
  isGenerating,
  disabled = false,
}) => {
  return (
    <div className="rounded-2xl border border-white/[0.08] bg-[#0E1320]/80 p-5 shadow-2xl backdrop-blur-xl">
      <div className="flex items-center justify-between border-b border-white/[0.06] pb-3 mb-4">
        <div className="flex items-center space-x-2">
          <span className="flex h-2.5 w-2.5 rounded-full bg-indigo-400" />
          <h2 className="text-sm font-semibold text-white tracking-wide uppercase">
            Voice Parameters & Controls (नियंत्रण)
          </h2>
        </div>
        <span className="text-[11px] text-slate-400">
          Direct Parler-TTS conditioning tokens
        </span>
      </div>

      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {/* Speed Slider */}
        <div className="space-y-2 rounded-xl bg-[#0B0E17] p-3.5 border border-white/[0.04]">
          <div className="flex items-center justify-between text-xs">
            <span className="flex items-center space-x-1.5 font-medium text-slate-300">
              <Gauge className="h-3.5 w-3.5 text-primary-400" />
              <span>Speed / Pace (गति)</span>
            </span>
            <span className="rounded bg-primary-500/10 px-2 py-0.5 text-xs font-bold text-primary-400">
              {speed.toFixed(2)}x
            </span>
          </div>
          <input
            type="range"
            min="0.7"
            max="1.4"
            step="0.05"
            value={speed}
            disabled={disabled || isGenerating}
            onChange={(e) => setSpeed(parseFloat(e.target.value))}
            className="w-full cursor-pointer h-1.5 rounded-lg bg-slate-700"
          />
          <div className="flex justify-between text-[10px] text-slate-500">
            <span>Slow (0.7x)</span>
            <span>Normal (1.0x)</span>
            <span>Fast (1.4x)</span>
          </div>
        </div>

        {/* Pitch Level */}
        <div className="space-y-2 rounded-xl bg-[#0B0E17] p-3.5 border border-white/[0.04]">
          <div className="flex items-center justify-between text-xs">
            <span className="flex items-center space-x-1.5 font-medium text-slate-300">
              <Activity className="h-3.5 w-3.5 text-accent-purple" />
              <span>Vocal Pitch (तारत्व)</span>
            </span>
          </div>
          <div className="grid grid-cols-3 gap-1.5 pt-1">
            {(['low', 'moderate', 'high'] as PitchLevel[]).map((p) => (
              <button
                key={p}
                type="button"
                disabled={disabled || isGenerating}
                onClick={() => setPitch(p)}
                className={`rounded-lg py-1.5 text-xs font-medium capitalize transition border ${
                  pitch === p
                    ? 'border-accent-purple bg-accent-purple/20 text-white'
                    : 'border-white/[0.06] bg-white/[0.02] text-slate-400 hover:bg-white/[0.06] hover:text-white'
                }`}
              >
                {p === 'low' ? 'Low' : p === 'moderate' ? 'Mid' : 'High'}
              </button>
            ))}
          </div>
        </div>

        {/* Speaking Style */}
        <div className="space-y-2 rounded-xl bg-[#0B0E17] p-3.5 border border-white/[0.04]">
          <div className="flex items-center justify-between text-xs">
            <span className="flex items-center space-x-1.5 font-medium text-slate-300">
              <Sparkles className="h-3.5 w-3.5 text-pink-400" />
              <span>Style / Emotion (शैली)</span>
            </span>
          </div>
          <select
            value={style}
            disabled={disabled || isGenerating}
            onChange={(e) => setStyle(e.target.value as SpeakingStyle)}
            className="w-full rounded-lg border border-white/[0.08] bg-[#121724] px-3 py-1.5 text-xs font-medium text-slate-200 focus:border-primary-500 focus:outline-none"
          >
            <option value="natural">Natural & Engaging (प्राकृतिक)</option>
            <option value="expressive">Expressive & Emotive (भावपूर्ण)</option>
            <option value="monotone">Monotone & Steady (शांत/गंभीर)</option>
            <option value="urgent">Urgent & Dynamic (त्वरित)</option>
          </select>
        </div>

        {/* Output Format */}
        <div className="space-y-2 rounded-xl bg-[#0B0E17] p-3.5 border border-white/[0.04]">
          <div className="flex items-center justify-between text-xs">
            <span className="flex items-center space-x-1.5 font-medium text-slate-300">
              <Volume2 className="h-3.5 w-3.5 text-emerald-400" />
              <span>Audio Format (प्रारूप)</span>
            </span>
          </div>
          <div className="grid grid-cols-2 gap-1.5 pt-1">
            {(['mp3', 'wav'] as AudioFormat[]).map((fmt) => (
              <button
                key={fmt}
                type="button"
                disabled={disabled || isGenerating}
                onClick={() => setAudioFormat(fmt)}
                className={`rounded-lg py-1.5 text-xs font-bold uppercase transition border ${
                  audioFormat === fmt
                    ? 'border-emerald-500 bg-emerald-500/20 text-emerald-300'
                    : 'border-white/[0.06] bg-white/[0.02] text-slate-400 hover:bg-white/[0.06] hover:text-white'
                }`}
              >
                {fmt}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Primary Action Button */}
      <div className="mt-6 flex flex-col sm:flex-row items-center justify-between gap-4 border-t border-white/[0.06] pt-4">
        <div className="text-xs text-slate-400 flex items-center gap-1.5">
          <Sparkles className="h-3.5 w-3.5 text-amber-400" />
          <span>Generating uses CPU threadpool with dynamic attention conditioning.</span>
        </div>

        <button
          type="button"
          onClick={onGenerate}
          disabled={disabled || isGenerating}
          className="w-full sm:w-auto min-w-[240px] flex items-center justify-center space-x-2.5 rounded-xl bg-gradient-to-r from-primary-600 via-indigo-600 to-accent-purple px-6 py-3.5 text-sm font-bold text-white shadow-lg shadow-primary-500/25 transition hover:brightness-110 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isGenerating ? (
            <>
              <div className="h-4 w-4 rounded-full border-2 border-white border-t-transparent animate-spin" />
              <span>Synthesizing Speech... (आवाज़ बन रही है)</span>
            </>
          ) : (
            <>
              <Wand2 className="h-4 w-4" />
              <span>Generate Speech (आवाज़ उत्पन्न करें)</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
};
