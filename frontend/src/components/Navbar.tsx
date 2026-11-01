'use client';

import React, { useState } from 'react';
import {
  AudioWaveform,
  Cpu,
  History,
  Library,
  Menu,
  Mic2,
  Settings,
  Sparkles,
  Volume2,
  X,
} from 'lucide-react';
import { HealthResponse } from '@/types/tts';

interface NavbarProps {
  activeTab: 'tts' | 'library' | 'history';
  setActiveTab: (tab: 'tts' | 'library' | 'history') => void;
  onOpenSettings: () => void;
  health: HealthResponse | null;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  onOpenSettings,
  health,
}) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40 w-full border-b border-white/[0.08] bg-[#080B11]/80 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Brand Logo */}
        <div
          onClick={() => setActiveTab('tts')}
          className="flex cursor-pointer items-center space-x-3 transition hover:opacity-90"
        >
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-primary-600 via-accent-purple to-pink-500 shadow-lg shadow-primary-500/25">
            <AudioWaveform className="h-5 w-5 text-white" />
          </div>
          <div className="flex flex-col">
            <div className="flex items-center space-x-1.5">
              <span className="text-xl font-bold tracking-tight text-white">
                HindiVoice
              </span>
              <span className="rounded-md bg-gradient-to-r from-primary-500 to-accent-purple px-1.5 py-0.5 text-[10px] font-semibold text-white uppercase tracking-wider">
                AI
              </span>
            </div>
            <span className="text-[11px] font-medium text-slate-400">
              प्राकृतिक हिंदी वाक् संश्लेषण (Indic Parler-TTS)
            </span>
          </div>
        </div>

        {/* Desktop Navigation Navigation */}
        <nav className="hidden md:flex items-center space-x-1">
          <button
            onClick={() => setActiveTab('tts')}
            className={`flex items-center space-x-2 rounded-lg px-4 py-2 text-sm font-medium transition ${
              activeTab === 'tts'
                ? 'bg-primary-600/20 text-primary-300 border border-primary-500/30'
                : 'text-slate-300 hover:bg-white/[0.04] hover:text-white'
            }`}
          >
            <Mic2 className="h-4 w-4" />
            <span>Text to Speech</span>
          </button>

          <button
            onClick={() => setActiveTab('library')}
            className={`flex items-center space-x-2 rounded-lg px-4 py-2 text-sm font-medium transition ${
              activeTab === 'library'
                ? 'bg-primary-600/20 text-primary-300 border border-primary-500/30'
                : 'text-slate-300 hover:bg-white/[0.04] hover:text-white'
            }`}
          >
            <Library className="h-4 w-4" />
            <span>Voice Library</span>
          </button>

          <button
            onClick={() => setActiveTab('history')}
            className={`flex items-center space-x-2 rounded-lg px-4 py-2 text-sm font-medium transition ${
              activeTab === 'history'
                ? 'bg-primary-600/20 text-primary-300 border border-primary-500/30'
                : 'text-slate-300 hover:bg-white/[0.04] hover:text-white'
            }`}
          >
            <History className="h-4 w-4" />
            <span>History</span>
          </button>
        </nav>

        {/* Right side: Status Badge & Settings */}
        <div className="hidden sm:flex items-center space-x-3">
          {/* Hardware & Backend Status */}
          <div
            className={`flex items-center space-x-2 rounded-full px-3 py-1 text-xs font-medium border ${
              health?.status === 'ready'
                ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400'
                : health?.status === 'loading'
                ? 'border-amber-500/30 bg-amber-500/10 text-amber-400'
                : 'border-slate-700 bg-slate-800/60 text-slate-400'
            }`}
          >
            <span
              className={`h-2 w-2 rounded-full ${
                health?.status === 'ready'
                  ? 'bg-emerald-400 animate-pulse'
                  : health?.status === 'loading'
                  ? 'bg-amber-400 animate-ping'
                  : 'bg-slate-500'
              }`}
            />
            <span className="flex items-center gap-1">
              <Cpu className="h-3 w-3" />
              {health?.status === 'ready'
                ? `Engine Ready (${health.device.toUpperCase()})`
                : health?.status === 'loading'
                ? 'Warming Model...'
                : 'Connecting...'}
            </span>
          </div>

          <button
            onClick={onOpenSettings}
            className="flex h-9 w-9 items-center justify-center rounded-lg border border-white/[0.08] bg-white/[0.03] text-slate-300 transition hover:bg-white/[0.08] hover:text-white"
            title="Settings & System Telemetry"
          >
            <Settings className="h-4 w-4" />
          </button>
        </div>

        {/* Mobile Menu Button */}
        <div className="flex md:hidden items-center space-x-2">
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="flex h-9 w-9 items-center justify-center rounded-lg border border-white/[0.08] bg-white/[0.03] text-slate-300"
          >
            {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="border-b border-white/[0.08] bg-[#0A0E17] px-4 py-3 md:hidden space-y-2">
          <button
            onClick={() => {
              setActiveTab('tts');
              setMobileMenuOpen(false);
            }}
            className={`flex w-full items-center space-x-2 rounded-lg px-3 py-2 text-sm font-medium ${
              activeTab === 'tts'
                ? 'bg-primary-600/20 text-primary-300'
                : 'text-slate-300 hover:bg-white/[0.04]'
            }`}
          >
            <Mic2 className="h-4 w-4" />
            <span>Text to Speech</span>
          </button>
          <button
            onClick={() => {
              setActiveTab('library');
              setMobileMenuOpen(false);
            }}
            className={`flex w-full items-center space-x-2 rounded-lg px-3 py-2 text-sm font-medium ${
              activeTab === 'library'
                ? 'bg-primary-600/20 text-primary-300'
                : 'text-slate-300 hover:bg-white/[0.04]'
            }`}
          >
            <Library className="h-4 w-4" />
            <span>Voice Library</span>
          </button>
          <button
            onClick={() => {
              setActiveTab('history');
              setMobileMenuOpen(false);
            }}
            className={`flex w-full items-center space-x-2 rounded-lg px-3 py-2 text-sm font-medium ${
              activeTab === 'history'
                ? 'bg-primary-600/20 text-primary-300'
                : 'text-slate-300 hover:bg-white/[0.04]'
            }`}
          >
            <History className="h-4 w-4" />
            <span>History</span>
          </button>
          <button
            onClick={() => {
              onOpenSettings();
              setMobileMenuOpen(false);
            }}
            className="flex w-full items-center space-x-2 rounded-lg px-3 py-2 text-sm font-medium text-slate-300 hover:bg-white/[0.04]"
          >
            <Settings className="h-4 w-4" />
            <span>Settings</span>
          </button>
        </div>
      )}
    </header>
  );
};
