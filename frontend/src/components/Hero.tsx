'use client';

import React from 'react';
import { Bot, CheckCircle2, Download, Mic, Sparkles, Volume2 } from 'lucide-react';

export const Hero: React.FC = () => {
  return (
    <div className="relative overflow-hidden py-10 md:py-14 text-center">
      {/* Background glow effects */}
      <div className="pointer-events-none absolute left-1/2 top-0 -translate-x-1/2 -translate-y-1/2 h-[320px] w-[600px] rounded-full bg-gradient-to-r from-primary-600/20 via-accent-purple/20 to-pink-500/10 blur-[100px]" />

      <div className="relative mx-auto max-w-4xl px-4 sm:px-6">
        {/* Model Pill Badge */}
        <div className="inline-flex items-center space-x-2 rounded-full border border-primary-500/30 bg-primary-500/10 px-3.5 py-1.5 text-xs font-semibold text-primary-300 shadow-sm backdrop-blur-md">
          <Sparkles className="h-3.5 w-3.5 text-primary-400 animate-pulse" />
          <span>High-Energy Video Reel & Shorts TTS</span>
          <span className="text-white/40">•</span>
          <span className="text-slate-300">Hindi + Roman Hinglish Neural Voices</span>
        </div>

        {/* Heading */}
        <h1 className="mt-5 text-3xl font-extrabold tracking-tight text-white sm:text-5xl md:text-6xl">
          Hindi & Hinglish{' '}
          <span className="bg-gradient-to-r from-primary-400 via-indigo-300 to-purple-400 bg-clip-text text-transparent">
            AI Reel Voiceovers
          </span>
        </h1>

        {/* Description */}
        <p className="mt-4 text-base text-slate-300 sm:text-lg md:text-xl max-w-2xl mx-auto leading-relaxed font-devanagari">
          अपने हिंदी और Hinglish टेक्स्ट को 30-60 सेकंड के वायरल रील वॉइसओवर में बदलें। 
          स्वाभाविक उच्चारण, तकनीकी अंग्रेज़ी शब्द, और हाई-क्वालिटी ऑडियो डाउनलोड।
        </p>

        {/* Key Feature Badges */}
        <div className="mt-6 flex flex-wrap items-center justify-center gap-3 text-xs sm:text-sm text-slate-400">
          <div className="flex items-center space-x-1.5 rounded-lg bg-white/[0.03] border border-white/[0.06] px-3 py-1.5">
            <CheckCircle2 className="h-4 w-4 text-emerald-400" />
            <span>30s & 60s Reel Voiceovers</span>
          </div>
          <div className="flex items-center space-x-1.5 rounded-lg bg-white/[0.03] border border-white/[0.06] px-3 py-1.5">
            <CheckCircle2 className="h-4 w-4 text-indigo-400" />
            <span>Full Hinglish & English Terms</span>
          </div>
          <div className="flex items-center space-x-1.5 rounded-lg bg-white/[0.03] border border-white/[0.06] px-3 py-1.5">
            <CheckCircle2 className="h-4 w-4 text-accent-purple" />
            <span>6 Diverse Creator Voices</span>
          </div>
          <div className="flex items-center space-x-1.5 rounded-lg bg-white/[0.03] border border-white/[0.06] px-3 py-1.5">
            <CheckCircle2 className="h-4 w-4 text-pink-400" />
            <span>WAV & MP3 Downloads</span>
          </div>
        </div>
      </div>
    </div>
  );
};
