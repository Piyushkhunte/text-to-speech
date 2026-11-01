import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'HindiVoice AI - Professional Hindi Text-to-Speech',
  description:
    'Turn your Hindi text into natural, realistic AI speech using Indic Parler-TTS with multiple authentic male and female voices.',
  keywords: ['Hindi TTS', 'Text to Speech', 'Hindi AI Voice', 'AI4Bharat', 'Indic Parler-TTS', 'ElevenLabs Hindi'],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="hi" className="dark">
      <body className="min-h-screen bg-[#080B11] text-slate-100 antialiased selection:bg-primary-600 selection:text-white">
        {children}
      </body>
    </html>
  );
}
