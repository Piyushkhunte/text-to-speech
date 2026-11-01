'use client';

import React, { useRef, useState } from 'react';
import {
  Clock,
  Download,
  Edit2,
  Check,
  X,
  FileEdit,
  History,
  Mic,
  Pause,
  Play,
  RotateCcw,
  Search,
  Star,
  Trash2,
  Volume2,
} from 'lucide-react';
import { HistoryItem } from '@/types/tts';
import {
  deleteHistoryItem,
  getAudioDownloadUrl,
  getAudioStreamUrl,
  updateHistoryItem,
} from '@/services/api';

interface HistoryPanelProps {
  history: HistoryItem[];
  onRefresh: () => void;
  onLoadIntoEditor?: (item: HistoryItem) => void;
}

export const HistoryPanel: React.FC<HistoryPanelProps> = ({
  history,
  onRefresh,
  onLoadIntoEditor,
}) => {
  const [playingId, setPlayingId] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [isDeletingId, setIsDeletingId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState<'all' | 'favorites'>('all');
  const [speakerFilter, setSpeakerFilter] = useState<string>('all');

  // Editing title state
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitleValue, setEditTitleValue] = useState<string>('');

  const togglePlay = (item: HistoryItem) => {
    if (playingId === item.id) {
      audioRef.current?.pause();
      setPlayingId(null);
    } else {
      if (audioRef.current) {
        audioRef.current.pause();
      }
      const streamUrl = getAudioStreamUrl(item.id, 'mp3');
      const audio = new Audio(streamUrl);
      audioRef.current = audio;
      setPlayingId(item.id);

      audio.play().catch((err) => {
        console.warn('Playback error:', err);
        setPlayingId(null);
      });

      audio.onended = () => setPlayingId(null);
      audio.onerror = () => setPlayingId(null);
    }
  };

  const handleToggleFavorite = async (item: HistoryItem, e: React.MouseEvent) => {
    e.stopPropagation();
    const newFavState = !item.is_favorite;
    try {
      await updateHistoryItem(item.id, { is_favorite: newFavState });
      onRefresh();
    } catch (err) {
      console.error('Failed to update favorite:', err);
    }
  };

  const startEditingTitle = (item: HistoryItem, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingId(item.id);
    setEditTitleValue(item.title || item.text.slice(0, 45));
  };

  const saveTitle = async (id: string, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    if (!editTitleValue.trim()) {
      setEditingId(null);
      return;
    }
    try {
      await updateHistoryItem(id, { title: editTitleValue.trim() });
      setEditingId(null);
      onRefresh();
    } catch (err) {
      console.error('Failed to save title:', err);
    }
  };

  const cancelEditing = (e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    setEditingId(null);
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this voiceover project?')) return;
    setIsDeletingId(id);
    try {
      if (playingId === id) {
        audioRef.current?.pause();
        setPlayingId(null);
      }
      await deleteHistoryItem(id);
      onRefresh();
    } catch (e) {
      console.error('Delete error:', e);
      alert('Could not delete history item.');
    } finally {
      setIsDeletingId(null);
    }
  };

  const formatTimestamp = (isoStr: string) => {
    try {
      const d = new Date(isoStr);
      return d.toLocaleString('en-IN', {
        dateStyle: 'medium',
        timeStyle: 'short',
      });
    } catch {
      return isoStr;
    }
  };

  // Filter items in memory based on search & tab
  const filteredHistory = history.filter((item) => {
    // 1. Tab filter
    if (activeTab === 'favorites' && !item.is_favorite) {
      return false;
    }
    // 2. Speaker filter
    if (speakerFilter !== 'all' && item.speaker_id !== speakerFilter) {
      return false;
    }
    // 3. Search query
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchText = (item.text || '').toLowerCase().includes(q);
      const matchTitle = (item.title || '').toLowerCase().includes(q);
      const matchSpeaker = (item.speaker_name || '').toLowerCase().includes(q);
      if (!matchText && !matchTitle && !matchSpeaker) return false;
    }
    return true;
  });

  const favoritesCount = history.filter((i) => i.is_favorite).length;

  return (
    <div className="rounded-2xl border border-white/[0.08] bg-[#0E1320]/80 p-6 shadow-2xl backdrop-blur-xl">
      {/* Header & CRUD Filters */}
      <div className="border-b border-white/[0.06] pb-5 mb-5 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <History className="h-5 w-5 text-primary-400" />
              <span>Voiceover Projects & History (प्रोजेक्ट और इतिहास)</span>
            </h2>
            <p className="mt-1 text-sm text-slate-400">
              Persistent SQLite database with full CRUD: rename projects, star favorites, reload into editor, or download audio.
            </p>
          </div>
          <span className="text-xs text-slate-400 font-medium bg-white/[0.04] px-3 py-1.5 rounded-lg border border-white/[0.04] self-start sm:self-auto">
            {history.length} Saved Generations
          </span>
        </div>

        {/* Filter Bar: Search + Tabs */}
        <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3 pt-2">
          {/* Tabs: All vs Favorites */}
          <div className="flex items-center gap-1.5 bg-[#090C14] p-1 rounded-xl border border-white/[0.06]">
            <button
              type="button"
              onClick={() => setActiveTab('all')}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition ${
                activeTab === 'all'
                  ? 'bg-primary-500/20 text-primary-300 border border-primary-500/30'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              All Projects ({history.length})
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('favorites')}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg transition ${
                activeTab === 'favorites'
                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                  : 'text-slate-400 hover:text-amber-300'
              }`}
            >
              <Star className="h-3.5 w-3.5 fill-current" />
              <span>Starred ({favoritesCount})</span>
            </button>
          </div>

          {/* Search Box */}
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by title, script text, or speaker..."
              className="w-full rounded-xl border border-white/[0.08] bg-[#090C14] py-2 pl-9 pr-8 text-xs text-slate-200 placeholder-slate-500 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            />
            {searchQuery && (
              <button
                type="button"
                onClick={() => setSearchQuery('')}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            )}
          </div>
        </div>
      </div>

      {filteredHistory.length === 0 ? (
        <div className="py-12 text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-white/[0.02] border border-white/[0.06] text-slate-500">
            <Clock className="h-6 w-6" />
          </div>
          <h4 className="mt-3 text-sm font-semibold text-slate-300">
            {searchQuery || activeTab === 'favorites'
              ? 'No matching generations found (कोई रिकॉर्ड नहीं मिला)'
              : 'No voiceover history yet (कोई पिछला रिकॉर्ड नहीं है)'}
          </h4>
          <p className="mt-1 text-xs text-slate-500">
            {searchQuery
              ? 'Try a different keyword or clear the search filter.'
              : 'Generate speech above and your projects will be saved here in SQLite with full CRUD controls.'}
          </p>
        </div>
      ) : (
        <div className="space-y-3.5">
          {filteredHistory.map((item) => {
            const isPlaying = playingId === item.id;
            const isDeleting = isDeletingId === item.id;
            const isEditing = editingId === item.id;

            return (
              <div
                key={item.id}
                className="flex flex-col md:flex-row md:items-center justify-between gap-4 rounded-xl border border-white/[0.06] bg-[#0B0E17] p-4 transition hover:border-white/[0.12] hover:bg-[#0D121F]"
              >
                {/* Left: Star + Play button & Title/Text */}
                <div className="flex items-start space-x-3.5 flex-1 min-w-0">
                  {/* Favorite Star Button */}
                  <button
                    type="button"
                    onClick={(e) => handleToggleFavorite(item, e)}
                    className={`mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border transition ${
                      item.is_favorite
                        ? 'border-amber-500/40 bg-amber-500/10 text-amber-400 hover:bg-amber-500/20'
                        : 'border-white/[0.04] bg-white/[0.02] text-slate-500 hover:text-amber-400 hover:border-amber-500/30'
                    }`}
                    title={item.is_favorite ? 'Remove from favorites' : 'Star as favorite'}
                  >
                    <Star
                      className={`h-4 w-4 ${item.is_favorite ? 'fill-amber-400' : ''}`}
                    />
                  </button>

                  {/* Play / Pause button */}
                  <button
                    type="button"
                    onClick={() => togglePlay(item)}
                    className={`mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-xl transition ${
                      isPlaying
                        ? 'bg-primary-500 text-white animate-pulse'
                        : 'bg-white/[0.05] text-slate-200 hover:bg-white/[0.1] hover:text-white'
                    }`}
                  >
                    {isPlaying ? (
                      <Pause className="h-4 w-4 fill-current" />
                    ) : (
                      <Play className="h-4 w-4 fill-current translate-x-0.5" />
                    )}
                  </button>

                  <div className="min-w-0 flex-1">
                    {/* Project Title (Inline Editable) */}
                    <div className="flex items-center gap-2">
                      {isEditing ? (
                        <div className="flex items-center gap-1.5 w-full max-w-md">
                          <input
                            type="text"
                            value={editTitleValue}
                            onChange={(e) => setEditTitleValue(e.target.value)}
                            onKeyDown={(e) => {
                              if (e.key === 'Enter') saveTitle(item.id);
                              if (e.key === 'Escape') cancelEditing();
                            }}
                            autoFocus
                            className="flex-1 rounded-lg border border-primary-500/50 bg-[#06080E] px-2.5 py-1 text-xs text-white focus:outline-none focus:ring-1 focus:ring-primary-500"
                          />
                          <button
                            type="button"
                            onClick={(e) => saveTitle(item.id, e)}
                            className="p-1 rounded bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30"
                            title="Save title"
                          >
                            <Check className="h-3.5 w-3.5" />
                          </button>
                          <button
                            type="button"
                            onClick={cancelEditing}
                            className="p-1 rounded bg-rose-500/20 text-rose-400 hover:bg-rose-500/30"
                            title="Cancel"
                          >
                            <X className="h-3.5 w-3.5" />
                          </button>
                        </div>
                      ) : (
                        <div className="flex items-center gap-2 group">
                          <h4 className="text-sm font-semibold text-white tracking-wide truncate">
                            {item.title || item.speaker_name}
                          </h4>
                          <button
                            type="button"
                            onClick={(e) => startEditingTitle(item, e)}
                            className="opacity-0 group-hover:opacity-100 transition p-1 text-slate-400 hover:text-primary-300"
                            title="Rename project title"
                          >
                            <Edit2 className="h-3 w-3" />
                          </button>
                        </div>
                      )}
                    </div>

                    {/* Script Snippet */}
                    <p className="mt-1 text-xs font-normal text-slate-300 font-devanagari line-clamp-2 leading-relaxed">
                      &ldquo;{item.text}&rdquo;
                    </p>

                    {/* Metadata tags */}
                    <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-slate-400">
                      <span className="font-semibold text-primary-300">
                        {item.speaker_name}
                      </span>
                      <span>•</span>
                      <span>{item.duration_seconds}s</span>
                      <span>•</span>
                      <span>{formatTimestamp(item.created_at)}</span>
                      <span>•</span>
                      <span className="rounded bg-white/[0.04] px-1.5 py-0.5 text-[10px] uppercase font-mono">
                        {item.speed}x • {item.pitch} • {item.style}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Right: Actions */}
                <div className="flex items-center space-x-2 self-end md:self-center shrink-0">
                  {/* Load into Editor Button */}
                  {onLoadIntoEditor && (
                    <button
                      type="button"
                      onClick={() => onLoadIntoEditor(item)}
                      className="flex items-center space-x-1 rounded-lg border border-indigo-500/30 bg-indigo-500/10 px-2.5 py-1.5 text-xs font-semibold text-indigo-300 transition hover:bg-indigo-500/20"
                      title="Load this script and voice into editor to iterate"
                    >
                      <RotateCcw className="h-3.5 w-3.5" />
                      <span className="hidden sm:inline">Load in Editor</span>
                    </button>
                  )}

                  <a
                    href={getAudioDownloadUrl(item.id, 'mp3')}
                    download={`hindivoice_${item.id.slice(0, 8)}.mp3`}
                    className="flex items-center space-x-1 rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-2.5 py-1.5 text-xs font-semibold text-emerald-400 transition hover:bg-emerald-500/20"
                    title="Download MP3"
                  >
                    <Download className="h-3.5 w-3.5" />
                    <span>MP3</span>
                  </a>

                  <a
                    href={getAudioDownloadUrl(item.id, 'wav')}
                    download={`hindivoice_${item.id.slice(0, 8)}.wav`}
                    className="flex items-center space-x-1 rounded-lg border border-primary-500/30 bg-primary-500/10 px-2.5 py-1.5 text-xs font-semibold text-primary-300 transition hover:bg-primary-500/20"
                    title="Download WAV"
                  >
                    <Download className="h-3.5 w-3.5" />
                    <span>WAV</span>
                  </a>

                  <button
                    type="button"
                    disabled={isDeleting}
                    onClick={() => handleDelete(item.id)}
                    className="flex h-8 w-8 items-center justify-center rounded-lg border border-white/[0.06] bg-white/[0.02] text-slate-400 transition hover:bg-rose-500/10 hover:text-rose-400 hover:border-rose-500/30 disabled:opacity-40"
                    title="Delete record from SQLite database"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
