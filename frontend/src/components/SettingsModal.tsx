'use client';

import React from 'react';
import {
  CheckCircle,
  Cpu,
  HardDrive,
  Info,
  Shield,
  X,
} from 'lucide-react';
import { HealthResponse } from '@/types/tts';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  health: HealthResponse | null;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
  health,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-md animate-fade-in">
      <div className="relative w-full max-w-lg rounded-2xl border border-white/[0.1] bg-[#0E1320] p-6 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-white/[0.08] pb-4">
          <div className="flex items-center space-x-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary-500/10 text-primary-400 border border-primary-500/20">
              <Cpu className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">System Settings & Telemetry</h3>
              <p className="text-xs text-slate-400">HindiVoice AI Architecture Details</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 hover:bg-white/[0.06] hover:text-white"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Content */}
        <div className="mt-5 space-y-4 text-xs">
          {/* AI Model Spec */}
          <div className="rounded-xl bg-[#090C14] p-3.5 border border-white/[0.04] space-y-2">
            <span className="font-semibold text-slate-300 flex items-center gap-1.5">
              <Info className="h-3.5 w-3.5 text-indigo-400" />
              AI Model Information
            </span>
            <div className="grid grid-cols-2 gap-2 text-slate-400">
              <div>
                <span className="text-slate-500 block">Model Repository:</span>
                <span className="font-mono text-slate-200">ai4bharat/indic-parler-tts</span>
              </div>
              <div>
                <span className="text-slate-500 block">Architecture:</span>
                <span className="text-slate-200">Parler-TTS (0.9B params)</span>
              </div>
              <div>
                <span className="text-slate-500 block">Status:</span>
                <span className="text-emerald-400 font-medium">
                  {health?.status === 'ready' ? 'Loaded in Memory' : health?.status || 'Connecting...'}
                </span>
              </div>
              <div>
                <span className="text-slate-500 block">License:</span>
                <span className="text-slate-200">Apache 2.0 (Open-Source)</span>
              </div>
            </div>
          </div>

          {/* Hardware & Compute */}
          <div className="rounded-xl bg-[#090C14] p-3.5 border border-white/[0.04] space-y-2">
            <span className="font-semibold text-slate-300 flex items-center gap-1.5">
              <Cpu className="h-3.5 w-3.5 text-accent-purple" />
              Hardware & Compute Environment
            </span>
            <div className="grid grid-cols-2 gap-2 text-slate-400">
              <div>
                <span className="text-slate-500 block">Execution Device:</span>
                <span className="font-mono uppercase font-bold text-primary-400">
                  {health?.device || 'CPU'}
                </span>
              </div>
              <div>
                <span className="text-slate-500 block">CPU Logical Cores:</span>
                <span className="text-slate-200">{health?.cpu_cores || 'N/A'} Cores</span>
              </div>
              <div>
                <span className="text-slate-500 block">GPU Acceleration:</span>
                <span className="text-slate-300">
                  {health?.gpu_available ? `Active (${health.gpu_name})` : 'Integrated GPU (CPU Fallback)'}
                </span>
              </div>
              <div>
                <span className="text-slate-500 block">Server Uptime:</span>
                <span className="text-slate-200 font-mono">
                  {health?.uptime_seconds ? `${Math.round(health.uptime_seconds)}s` : 'N/A'}
                </span>
              </div>
            </div>
          </div>

          {/* Gemini AI Pro Plan TTS Configuration */}
          <div className="rounded-xl bg-gradient-to-br from-indigo-950/40 to-purple-950/20 p-3.5 border border-indigo-500/20 space-y-2">
            <span className="font-semibold text-indigo-300 flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <Shield className="h-3.5 w-3.5 text-indigo-400" />
                Google Gemini AI TTS Engine
              </span>
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                health?.device === 'cloud-gemini'
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                  : 'bg-white/[0.06] text-slate-400'
              }`}>
                {health?.device === 'cloud-gemini' ? 'Gemini 3.8 Active' : 'Ready for API Key'}
              </span>
            </span>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              To use your Google AI Pro Plan for studio-grade voice generation, simply paste your key into <code className="bg-white/[0.08] px-1 py-0.5 rounded text-indigo-300">.env</code>:
            </p>
            <div className="rounded-lg bg-black/50 p-2 font-mono text-[11px] text-indigo-200 border border-white/[0.04] select-all">
              GEMINI_API_KEY=AIzaSy...
            </div>
            <p className="text-slate-500 text-[10px]">
              When configured, the backend automatically uses <strong className="text-slate-300">gemini-3.8-flash-tts</strong>. If empty or quota is exceeded, it falls back seamlessly to the local neural engine.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-6 border-t border-white/[0.08] pt-4 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="rounded-xl bg-white/[0.06] px-4 py-2 text-xs font-semibold text-slate-200 hover:bg-white/[0.1] hover:text-white transition"
          >
            Close Settings
          </button>
        </div>
      </div>
    </div>
  );
};
