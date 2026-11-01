'use client';

import React, { useMemo } from 'react';
import { AlertCircle, Check, Clipboard, Sparkles, Trash2 } from 'lucide-react';

interface TextInputEditorProps {
  text: string;
  onChange: (val: string) => void;
  maxLength?: number;
  disabled?: boolean;
}

const SAMPLE_PROMPTS = [
  {
    title: '📱 WhatsApp Reel (Curious → Story → Reveal → Ending)',
    text: `**[Hook — curious, energetic]**

Socho, tumne WhatsApp par apne dost ko message bheja…  
"Kal milte hain!"

Lekin kya tumne kabhi socha hai, ye message uske phone tak pahunchta kaise hai?

**[Story begins]**

Sabse pehle, tumhara message tumhare phone se WhatsApp ke system tak jaata hai.

Lekin ek interesting baat hai…

Tumhara message end-to-end encrypted hota hai. Matlab, message ka content sirf sender aur receiver ke devices hi padh sakte hain.

Ab WhatsApp ka server message ko sahi destination tak pahunchane mein help karta hai.

Agar dost online hai, message uske device tak deliver ho jaata hai.

Aur agar offline hai? Toh encrypted message temporarily server par wait kar sakta hai, jab tak uska device available na ho.

**[Reveal — slightly dramatic]**

Aur bas, isi process mein networking, servers, encryption aur databases jaise concepts ka role samajh aata hai.

**[Ending]**

Agli baar WhatsApp par message bhejo, toh yaad rakhna… ek simple text ke peeche poora software system kaam kar raha hota hai!

Aise tech concepts simple stories mein samajhne ke liye follow karo **Code Ki Class!**`,
  },
  {
    title: '🔥 System Design Reel (YouTube Style)',
    text: 'इंटरव्यूअर ने पूछा Google जैसा सर्च डिजाइन करो। तुमने कहा हर बार पूरा इंटरनेट स्कैन कर लो। बस यहीं पर राउंड हाथ से जा सकता है! असली डिज़ाइन तीन पार्ट्स में चलता है। क्रॉलर पेजेस लाता है, इंडेक्सर उल्टा इंडेक्स बनाता है और रैंकिंग से पहला पेज डिसाइड होता है। ऑटो कंप्लीट पहले ही शुरू हो जाता है!',
  },
  {
    title: '⚡ 30s Reel (Hinglish Hook)',
    text: 'Kya aapne kabhi socha hai ki programming me ek sath kai saari values kaise store karte hain? Iska simple answer hai Arrays aur Lists! Chaliye 30 seconds me samajhte hain ki computer memory me yeh data kaise arrange hota hai.',
  },
  {
    title: '🎬 60s Reel (Tech Explainer)',
    text: 'नमस्ते दोस्तों! क्या आपने कभी सोचा है कि Programming में एक साथ कई सारे values कैसे store करते हैं? जब हमें हजारों users का data manage करना होता है, तो हम Arrays और Data Structures का use करते हैं। यह technique memory को fast और efficient बनाती है। अगर आपको यह concept समझ आया, तो like और save ज़रूर करें!',
  },
];

export const TextInputEditor: React.FC<TextInputEditorProps> = ({
  text,
  onChange,
  maxLength = 3000,
  disabled = false,
}) => {
  // Compute word and character counts
  const charCount = text.length;
  const wordCount = useMemo(() => {
    const trimmed = text.trim();
    if (!trimmed) return 0;
    return trimmed.split(/\s+/).length;
  }, [text]);

  // Check if narrative scene tags are present (Director Mode)
  const isDirectorMode = useMemo(() => {
    return /(?:hook|story|reveal|ending|dramatic|curious)\b/i.test(text) && /\[[^\]]+\]/.test(text);
  }, [text]);

  // Estimate reel voiceover duration (~2.5 words per second standard video pace)
  const estimatedSeconds = useMemo(() => {
    if (wordCount === 0) return 0;
    return Math.max(1, Math.round(wordCount / 2.5));
  }, [wordCount]);

  // Check language style
  const hasDevanagari = useMemo(() => /[\u0900-\u097F]/.test(text), [text]);
  const hasLatin = useMemo(() => /[a-zA-Z]/.test(text), [text]);

  const scriptType = useMemo(() => {
    if (!text.trim()) return null;
    if (hasDevanagari && hasLatin) return 'Mixed Hindi + English (Hinglish)';
    if (hasDevanagari) return 'Devanagari Hindi';
    if (hasLatin) return 'Roman Hinglish';
    return 'Text';
  }, [hasDevanagari, hasLatin, text]);

  // Reel target helper
  const reelBadge = useMemo(() => {
    if (estimatedSeconds === 0) return null;
    if (estimatedSeconds <= 35) {
      return {
        label: `⚡ ~${estimatedSeconds}s (Perfect for 30s Reel / Short)`,
        color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
      };
    }
    if (estimatedSeconds <= 65) {
      return {
        label: `🎬 ~${estimatedSeconds}s (Perfect for 60s Reel / YouTube Short)`,
        color: 'text-indigo-400 bg-indigo-500/10 border-indigo-500/20',
      };
    }
    return {
      label: `📹 ~${estimatedSeconds}s (Long-form Video Voiceover)`,
      color: 'text-purple-400 bg-purple-500/10 border-purple-500/20',
    };
  }, [estimatedSeconds]);

  // Validation state
  const isOverLimit = charCount > maxLength;

  const handlePaste = async () => {
    try {
      const clipText = await navigator.clipboard.readText();
      if (clipText) {
        onChange(clipText.slice(0, maxLength));
      }
    } catch (e) {
      console.warn('Clipboard read error:', e);
    }
  };

  const handleClear = () => {
    onChange('');
  };

  return (
    <div className="rounded-2xl border border-white/[0.08] bg-[#0E1320]/80 p-5 shadow-2xl backdrop-blur-xl">
      {/* Editor Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/[0.06] pb-3 mb-3">
        <div className="flex items-center space-x-2.5">
          <span className="flex h-2.5 w-2.5 rounded-full bg-primary-500 animate-pulse" />
          <h2 className="text-sm font-semibold text-white tracking-wide uppercase">
            Hindi & Hinglish Reel Script Editor (टेक्स्ट संपादक)
          </h2>
          {scriptType && (
            <span className="hidden sm:inline-block rounded-md bg-white/[0.06] px-2 py-0.5 text-[11px] font-medium text-slate-300 border border-white/[0.08]">
              {scriptType}
            </span>
          )}
        </div>

        {/* Action Controls & Reel Duration Indicator */}
        <div className="flex items-center space-x-2">
          {reelBadge && (
            <div
              className={`hidden md:flex items-center rounded-lg border px-2.5 py-1 text-xs font-semibold ${reelBadge.color}`}
            >
              {reelBadge.label}
            </div>
          )}
          <button
            type="button"
            onClick={handlePaste}
            disabled={disabled}
            className="flex items-center space-x-1.5 rounded-lg border border-white/[0.08] bg-white/[0.03] px-2.5 py-1.5 text-xs font-medium text-slate-300 transition hover:bg-white/[0.08] hover:text-white disabled:opacity-40"
          >
            <Clipboard className="h-3.5 w-3.5" />
            <span>Paste (पेस्ट)</span>
          </button>
          <button
            type="button"
            onClick={handleClear}
            disabled={disabled || charCount === 0}
            className="flex items-center space-x-1.5 rounded-lg border border-white/[0.08] bg-white/[0.03] px-2.5 py-1.5 text-xs font-medium text-slate-300 transition hover:bg-rose-500/10 hover:text-rose-400 hover:border-rose-500/30 disabled:opacity-40"
          >
            <Trash2 className="h-3.5 w-3.5" />
            <span>Clear (हटाएं)</span>
          </button>
        </div>
      </div>

      {/* Reel Duration Badge on Mobile */}
      {reelBadge && (
        <div className="md:hidden mb-2.5">
          <div
            className={`inline-flex items-center rounded-lg border px-2.5 py-1 text-xs font-semibold ${reelBadge.color}`}
          >
            {reelBadge.label}
          </div>
        </div>
      )}

      {/* Emotion Scene Tag Inserters (Director Mode) */}
      <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="text-[11px] font-medium text-slate-400">🎬 सीन टैग्स (Acting Beats):</span>
          <button
            type="button"
            disabled={disabled}
            onClick={() => onChange(text + (text ? '\n\n' : '') + '**[Hook — curious, energetic]**\n')}
            className="rounded-md border border-amber-500/30 bg-amber-500/10 px-2 py-0.5 text-[11px] font-semibold text-amber-300 transition hover:bg-amber-500/20"
          >
            + [Hook — Curious]
          </button>
          <button
            type="button"
            disabled={disabled}
            onClick={() => onChange(text + (text ? '\n\n' : '') + '**[Story begins]**\n')}
            className="rounded-md border border-sky-500/30 bg-sky-500/10 px-2 py-0.5 text-[11px] font-semibold text-sky-300 transition hover:bg-sky-500/20"
          >
            + [Story Begins]
          </button>
          <button
            type="button"
            disabled={disabled}
            onClick={() => onChange(text + (text ? '\n\n' : '') + '**[Reveal — slightly dramatic]**\n')}
            className="rounded-md border border-purple-500/30 bg-purple-500/10 px-2 py-0.5 text-[11px] font-semibold text-purple-300 transition hover:bg-purple-500/20"
          >
            + [Reveal — Dramatic]
          </button>
          <button
            type="button"
            disabled={disabled}
            onClick={() => onChange(text + (text ? '\n\n' : '') + '**[Ending]**\n')}
            className="rounded-md border border-emerald-500/30 bg-emerald-500/10 px-2 py-0.5 text-[11px] font-semibold text-emerald-300 transition hover:bg-emerald-500/20"
          >
            + [Ending — CTA]
          </button>
        </div>

        {isDirectorMode && (
          <span className="inline-flex items-center space-x-1 rounded-md border border-indigo-500/40 bg-indigo-500/15 px-2 py-0.5 text-[11px] font-bold text-indigo-300 animate-pulse">
            <span>✨ Director Mode Active (Multi-Scene Voice Acting)</span>
          </span>
        )}
      </div>

      {/* Text Area */}
      <div className="relative">
        <textarea
          value={text}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
          rows={7}
          placeholder="यहाँ अपना रील स्क्रिप्ट लिखें... [Hook], [Story], [Reveal], [Ending] जैसे सीन टैग्स का उपयोग करके भावनात्मक आवाज़ बदलें..."
          className="w-full resize-y rounded-xl border border-white/[0.06] bg-[#0A0D16] p-4 text-base md:text-lg font-devanagari text-slate-100 placeholder-slate-500 focus:border-primary-500/60 focus:bg-[#0B0F1A] focus:outline-none focus:ring-2 focus:ring-primary-500/20 disabled:cursor-not-allowed disabled:opacity-50 leading-relaxed tracking-normal"
        />
      </div>

      {/* Validation alert */}
      {isOverLimit && (
        <div className="mt-2.5 flex items-center space-x-2 text-xs text-rose-400">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>
            अधिकतम वर्ण सीमा {maxLength} है। वर्तमान: {charCount} वर्ण। कृपया टेक्स्ट छोटा करें।
          </span>
        </div>
      )}

      {/* Editor Footer: Sample Chips & Word/Char counters */}
      <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between border-t border-white/[0.04] pt-3">
        {/* Sample Reel Script Chips */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-medium text-slate-400">रील स्क्रिप्ट (Try):</span>
          {SAMPLE_PROMPTS.map((sample, idx) => (
            <button
              key={idx}
              type="button"
              disabled={disabled}
              onClick={() => onChange(sample.text)}
              className="rounded-lg border border-primary-500/20 bg-primary-500/5 px-2.5 py-1 text-xs font-medium text-primary-300 transition hover:bg-primary-500/15 hover:border-primary-500/40"
            >
              {sample.title}
            </button>
          ))}
        </div>

        {/* Counter Badges */}
        <div className="flex items-center space-x-4 self-end sm:self-auto text-xs font-medium text-slate-400">
          <span className="text-slate-300 font-semibold">{wordCount} शब्द (words)</span>
          <span
            className={`${
              isOverLimit ? 'font-bold text-rose-400' : 'text-slate-400'
            }`}
          >
            {charCount}/{maxLength} वर्ण (chars)
          </span>
        </div>
      </div>
    </div>
  );
};
