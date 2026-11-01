'use client';

import React, { useEffect, useRef, useState } from 'react';
import {
  Download,
  FileAudio,
  Pause,
  Play,
  RotateCcw,
  Sparkles,
  Volume2,
  VolumeX,
} from 'lucide-react';
import { TTSGenerateResponse } from '@/types/tts';
import { getAudioDownloadUrl, getAudioStreamUrl } from '@/services/api';

interface AudioPlayerProps {
  generation: TTSGenerateResponse | null;
}

export const AudioPlayer: React.FC<AudioPlayerProps> = ({ generation }) => {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);

  useEffect(() => {
    if (!generation) return;

    // Reset player on new generation
    setIsPlaying(false);
    setCurrentTime(0);

    const streamUrl = getAudioStreamUrl(generation.audio_id, 'mp3');
    const audio = new Audio(streamUrl);
    audioRef.current = audio;

    audio.onloadedmetadata = () => {
      setDuration(audio.duration || generation.duration_seconds);
    };

    audio.ontimeupdate = () => {
      setCurrentTime(audio.currentTime);
    };

    audio.onended = () => {
      setIsPlaying(false);
      setCurrentTime(0);
    };

    // Autoplay new generated audio
    audio
      .play()
      .then(() => setIsPlaying(true))
      .catch((e) => {
        console.warn('Autoplay prevented or paused:', e);
        setIsPlaying(false);
      });

    return () => {
      audio.pause();
      audioRef.current = null;
    };
  }, [generation]);

  if (!generation) {
    return (
      <div className="rounded-2xl border border-dashed border-white/[0.08] bg-[#0E1320]/40 p-8 text-center backdrop-blur-xl">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-white/[0.03] border border-white/[0.06] text-slate-500">
          <FileAudio className="h-7 w-7" />
        </div>
        <h3 className="mt-3 text-sm font-semibold text-slate-300">
          No Audio Generated Yet (कोई ऑडियो तैयार नहीं है)
        </h3>
        <p className="mt-1 text-xs text-slate-500 max-w-sm mx-auto">
          Type your Hindi text above, select a voice, and click &ldquo;Generate Speech&rdquo; to hear natural AI audio.
        </p>
      </div>
    );
  }

  const togglePlay = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current
        .play()
        .then(() => setIsPlaying(true))
        .catch(console.error);
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newTime = parseFloat(e.target.value);
    setCurrentTime(newTime);
    if (audioRef.current) {
      audioRef.current.currentTime = newTime;
    }
  };

  const handleRestart = () => {
    if (audioRef.current) {
      audioRef.current.currentTime = 0;
      audioRef.current.play().then(() => setIsPlaying(true));
    }
  };

  const toggleMute = () => {
    if (!audioRef.current) return;
    const nextMuted = !isMuted;
    setIsMuted(nextMuted);
    audioRef.current.muted = nextMuted;
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseFloat(e.target.value);
    setVolume(val);
    if (audioRef.current) {
      audioRef.current.volume = val;
      if (val === 0) setIsMuted(true);
      else if (isMuted) setIsMuted(false);
    }
  };

  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const totalDuration = duration || generation.duration_seconds || 1;
  const progressPercent = (currentTime / totalDuration) * 100;

  return (
    <div className="rounded-2xl border border-white/[0.1] bg-gradient-to-b from-[#131929] to-[#0D121F] p-6 shadow-2xl backdrop-blur-2xl">
      {/* Header Info */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-white/[0.06] pb-4 mb-5">
        <div>
          <div className="flex items-center space-x-2">
            <span className="flex h-2.5 w-2.5 rounded-full bg-emerald-400 animate-pulse" />
            <h3 className="text-base font-bold text-white tracking-wide">
              Generated Hindi Speech (उत्पन्न ऑडियो)
            </h3>
          </div>
          <div className="mt-1 flex items-center space-x-3 text-xs text-slate-400 font-devanagari">
            <span>वक्ता (Speaker): <strong className="text-primary-300 font-sans">{generation.speaker_name}</strong></span>
            <span>•</span>
            <span>अवधि: <strong>{generation.duration_seconds}s</strong></span>
            <span>•</span>
            <span>सैंपलिंग: <strong>{generation.sampling_rate} Hz</strong></span>
          </div>
        </div>

        {/* Download Buttons */}
        <div className="flex items-center space-x-2 self-start sm:self-auto">
          <a
            href={getAudioDownloadUrl(generation.audio_id, 'mp3')}
            download={`hindivoice_${generation.speaker_id}.mp3`}
            className="flex items-center space-x-1.5 rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-3 py-1.5 text-xs font-bold text-emerald-400 transition hover:bg-emerald-500/20 shadow-sm"
          >
            <Download className="h-3.5 w-3.5" />
            <span>MP3</span>
          </a>

          <a
            href={getAudioDownloadUrl(generation.audio_id, 'wav')}
            download={`hindivoice_${generation.speaker_id}.wav`}
            className="flex items-center space-x-1.5 rounded-xl border border-primary-500/30 bg-primary-500/10 px-3 py-1.5 text-xs font-bold text-primary-300 transition hover:bg-primary-500/20 shadow-sm"
          >
            <Download className="h-3.5 w-3.5" />
            <span>WAV</span>
          </a>
        </div>
      </div>

      {/* Animated Waveform Visualization */}
      <div className="mb-5 flex h-16 w-full items-center justify-between gap-1 overflow-hidden rounded-xl bg-[#090C14] px-4 py-2 border border-white/[0.04]">
        {Array.from({ length: 48 }).map((_, i) => {
          const barProgress = (i / 48) * 100;
          const isPassed = barProgress <= progressPercent;
          // Pseudo-random wave pattern based on index
          const baseHeight = 20 + Math.sin(i * 0.4) * 35 + ((i % 5) * 8);

          return (
            <div
              key={i}
              className={`w-full rounded-full transition-all duration-150 ${
                isPassed ? 'bg-gradient-to-t from-primary-500 to-accent-purple' : 'bg-slate-800'
              } ${isPlaying ? 'animate-pulse' : ''}`}
              style={{
                height: isPlaying ? `${Math.max(15, Math.min(95, baseHeight + (Math.random() * 20)))}%` : `${Math.max(15, baseHeight)}%`,
                opacity: isPassed ? 1 : 0.4,
              }}
            />
          );
        })}
      </div>

      {/* Scrub bar & Time stamps */}
      <div className="space-y-1.5">
        <input
          type="range"
          min="0"
          max={totalDuration}
          step="0.05"
          value={currentTime}
          onChange={handleSeek}
          className="w-full cursor-pointer h-2 rounded-lg bg-slate-800 accent-primary-500"
        />
        <div className="flex justify-between text-xs font-mono font-medium text-slate-400">
          <span>{formatTime(currentTime)}</span>
          <span>{formatTime(totalDuration)}</span>
        </div>
      </div>

      {/* Main Playback Controls */}
      <div className="mt-5 flex flex-wrap items-center justify-between gap-4 border-t border-white/[0.04] pt-4">
        <div className="flex items-center space-x-3">
          {/* Restart */}
          <button
            type="button"
            onClick={handleRestart}
            className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/[0.04] text-slate-300 transition hover:bg-white/[0.08] hover:text-white"
            title="Restart playback"
          >
            <RotateCcw className="h-4 w-4" />
          </button>

          {/* Big Play/Pause Button */}
          <button
            type="button"
            onClick={togglePlay}
            className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-tr from-primary-600 via-indigo-600 to-accent-purple text-white shadow-lg shadow-primary-500/30 transition hover:brightness-110 active:scale-95"
          >
            {isPlaying ? (
              <Pause className="h-5 w-5 fill-current" />
            ) : (
              <Play className="h-5 w-5 fill-current translate-x-0.5" />
            )}
          </button>
        </div>

        {/* Volume Slider */}
        <div className="flex items-center space-x-2 rounded-xl bg-white/[0.03] px-3 py-2 border border-white/[0.04]">
          <button
            type="button"
            onClick={toggleMute}
            className="text-slate-400 hover:text-white transition"
          >
            {isMuted || volume === 0 ? (
              <VolumeX className="h-4 w-4" />
            ) : (
              <Volume2 className="h-4 w-4" />
            )}
          </button>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={isMuted ? 0 : volume}
            onChange={handleVolumeChange}
            className="w-20 cursor-pointer h-1.5 rounded-lg bg-slate-700 accent-primary-500"
          />
        </div>
      </div>

      {/* Conditioning Prompt Telemetry */}
      {generation.conditioning_prompt && (
        <div className="mt-4 rounded-lg bg-black/30 p-2.5 text-[11px] text-slate-400 border border-white/[0.03]">
          <span className="font-semibold text-slate-300">Prompt Conditioning: </span>
          <span className="italic">{generation.conditioning_prompt}</span>
        </div>
      )}
    </div>
  );
};
