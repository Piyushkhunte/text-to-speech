'use client';

import React, { useEffect, useState } from 'react';
import {
  AudioPlayer,
} from '@/components/AudioPlayer';
import { Hero } from '@/components/Hero';
import { HistoryPanel } from '@/components/HistoryPanel';
import { Navbar } from '@/components/Navbar';
import { SettingsModal } from '@/components/SettingsModal';
import { TextInputEditor } from '@/components/TextInputEditor';
import { VoiceControls } from '@/components/VoiceControls';
import { VoiceLibrary } from '@/components/VoiceLibrary';
import { VoiceSelector } from '@/components/VoiceSelector';
import {
  deleteHistoryItem,
  fetchHealth,
  fetchHistory,
  fetchVoices,
  generateSpeech,
} from '@/services/api';
import {
  AudioFormat,
  HealthResponse,
  HistoryItem,
  PitchLevel,
  SpeakingStyle,
  TTSGenerateResponse,
  VoiceMetadata,
} from '@/types/tts';
import { AlertCircle } from 'lucide-react';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'tts' | 'library' | 'history'>('tts');
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [voices, setVoices] = useState<VoiceMetadata[]>([]);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  // TTS Parameters
  const [text, setText] = useState<string>(
    'इंटरव्यूअर ने पूछा Google जैसा सर्च डिजाइन करो। तुमने कहा हर बार पूरा इंटरनेट स्कैन कर लो। बस यहीं पर राउंड हाथ से जा सकता है! असली डिज़ाइन तीन पार्ट्स में चलता है।'
  );
  const [selectedVoiceId, setSelectedVoiceId] = useState<string>('aarav');
  const [speed, setSpeed] = useState<number>(1.0);
  const [pitch, setPitch] = useState<PitchLevel>('moderate');
  const [style, setStyle] = useState<SpeakingStyle>('natural');
  const [audioFormat, setAudioFormat] = useState<AudioFormat>('mp3');

  // Generation state
  const [isGenerating, setIsGenerating] = useState(false);
  const [lastGeneration, setLastGeneration] = useState<TTSGenerateResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Initial Data Fetching
  const loadInitialData = async () => {
    try {
      const [healthData, voicesData, historyData] = await Promise.all([
        fetchHealth().catch(() => null),
        fetchVoices().catch(() => null),
        fetchHistory().catch(() => null),
      ]);

      if (healthData) setHealth(healthData);
      if (voicesData && voicesData.voices) {
        setVoices(voicesData.voices);
        if (voicesData.default_voice) {
          setSelectedVoiceId(voicesData.default_voice);
        }
      }
      if (historyData && historyData.items) {
        setHistory(historyData.items);
      }
    } catch (e) {
      console.error('Initialization error:', e);
    }
  };

  useEffect(() => {
    loadInitialData();

    // Periodic health poll
    const interval = setInterval(async () => {
      try {
        const h = await fetchHealth();
        setHealth(h);
      } catch {
        // backend offline
      }
    }, 15000);

    return () => clearInterval(interval);
  }, []);

  const handleGenerate = async () => {
    if (!text.trim()) {
      setErrorMessage('कृपया कुछ हिंदी टेक्स्ट दर्ज करें। (Please enter Hindi text.)');
      return;
    }

    setErrorMessage(null);
    setIsGenerating(true);

    try {
      const response = await generateSpeech({
        text,
        speaker_id: selectedVoiceId,
        speed,
        pitch,
        style,
        audio_format: audioFormat,
      });

      setLastGeneration(response);

      // Refresh history in background
      fetchHistory()
        .then((h) => setHistory(h.items))
        .catch(console.warn);
    } catch (err: any) {
      console.error('Generation error:', err);
      setErrorMessage(
        err.message || 'वाक् उत्पन्न करने में त्रुटि हुई। कृपया पुनः प्रयास करें।'
      );
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSelectFromLibrary = (voiceId: string) => {
    setSelectedVoiceId(voiceId);
    setActiveTab('tts');
  };

  const handleLoadIntoEditor = (item: HistoryItem) => {
    setText(item.text);
    if (item.speaker_id) setSelectedVoiceId(item.speaker_id);
    if (item.speed) setSpeed(item.speed);
    if (item.pitch) setPitch(item.pitch as any);
    if (item.style) setStyle(item.style as any);
    setActiveTab('tts');
    window.scrollTo({ top: 300, behavior: 'smooth' });
  };

  return (
    <div className="flex min-h-screen flex-col bg-[#080B11] text-slate-100">
      {/* Navbar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenSettings={() => setIsSettingsOpen(true)}
        health={health}
      />

      <main className="flex-1 pb-16">
        {/* Hero Section */}
        <Hero />

        {/* Workspace Container */}
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          {/* Error Banner */}
          {errorMessage && (
            <div className="mb-6 flex items-center justify-between rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-rose-300">
              <div className="flex items-center space-x-2.5">
                <AlertCircle className="h-5 w-5 shrink-0 text-rose-400" />
                <span className="text-sm font-medium">{errorMessage}</span>
              </div>
              <button
                type="button"
                onClick={() => setErrorMessage(null)}
                className="text-xs text-rose-400 underline hover:text-rose-200"
              >
                Dismiss
              </button>
            </div>
          )}

          {/* TAB 1: Text to Speech Workspace */}
          {activeTab === 'tts' && (
            <div className="space-y-6">
              {/* 1. Text Editor */}
              <TextInputEditor
                text={text}
                onChange={setText}
                maxLength={3000}
                disabled={isGenerating}
              />

              {/* 2. Voice Selector */}
              <VoiceSelector
                voices={voices}
                selectedVoiceId={selectedVoiceId}
                onSelectVoice={setSelectedVoiceId}
                disabled={isGenerating}
              />

              {/* 3. Voice Controls & Action */}
              <VoiceControls
                speed={speed}
                setSpeed={setSpeed}
                pitch={pitch}
                setPitch={setPitch}
                style={style}
                setStyle={setStyle}
                audioFormat={audioFormat}
                setAudioFormat={setAudioFormat}
                onGenerate={handleGenerate}
                isGenerating={isGenerating}
                disabled={!text.trim()}
              />

              {/* 4. Audio Player */}
              <AudioPlayer generation={lastGeneration} />
            </div>
          )}

          {/* TAB 2: Voice Library */}
          {activeTab === 'library' && (
            <VoiceLibrary
              voices={voices}
              onSelectAndUse={handleSelectFromLibrary}
            />
          )}

          {/* TAB 3: History */}
          {activeTab === 'history' && (
            <HistoryPanel
              history={history}
              onRefresh={() => fetchHistory().then((h) => setHistory(h.items))}
              onLoadIntoEditor={handleLoadIntoEditor}
            />
          )}
        </div>
      </main>

      {/* Settings Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        health={health}
      />

      {/* Footer */}
      <footer className="border-t border-white/[0.06] bg-[#06080E] py-8 text-center text-xs text-slate-500">
        <div className="mx-auto max-w-7xl px-4">
          <p>© 2026 HindiVoice AI. Powered by open-source AI4Bharat Indic Parler-TTS.</p>
          <p className="mt-1">
            Production-grade Hindi speech synthesis • Apache 2.0 Open Source Model
          </p>
        </div>
      </footer>
    </div>
  );
}
