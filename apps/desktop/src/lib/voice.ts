// Voice Engine: Web Speech API Recognition (STT) + Synthesis (TTS) + Futuristic Sound Synthesizer

export interface VoiceState {
  isListening: boolean;
  isSpeaking: boolean;
  transcript: string;
  error: string | null;
}

class VoiceEngine {
  private recognition: any = null;
  private isListening = false;
  private isSpeaking = false;
  private audioCtx: AudioContext | null = null;

  constructor() {
    if (typeof window !== "undefined") {
      const SpeechRecognition =
        (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = true;
        this.recognition.lang = "en-US";
      }
    }
  }

  public isSupported(): boolean {
    return typeof window !== "undefined" && Boolean(
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition ||
      window.speechSynthesis
    );
  }

  public isSTTSupported(): boolean {
    return this.recognition !== null;
  }

  // Futuristic audio chimes synthesized using Web Audio API
  private playTone(freq: number, type: OscillatorType, duration: number, gainVal = 0.05) {
    try {
      if (!this.audioCtx) {
        const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
        if (AudioContextClass) this.audioCtx = new AudioContextClass();
      }
      if (!this.audioCtx) return;

      const osc = this.audioCtx.createOscillator();
      const gain = this.audioCtx.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(freq, this.audioCtx.currentTime);

      gain.gain.setValueAtTime(gainVal, this.audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, this.audioCtx.currentTime + duration);

      osc.connect(gain);
      gain.connect(this.audioCtx.destination);

      osc.start();
      osc.stop(this.audioCtx.currentTime + duration);
    } catch {
      // Audio autoplay policy fallback
    }
  }

  public playActivationChime() {
    this.playTone(587.33, "sine", 0.12, 0.06); // D5
    setTimeout(() => this.playTone(880, "sine", 0.18, 0.08), 90); // A5
  }

  public playDeactivationChime() {
    this.playTone(784, "sine", 0.12, 0.05); // G5
    setTimeout(() => this.playTone(440, "sine", 0.2, 0.04), 90); // A4
  }

  // Start listening to microphone
  public startListening(
    onResult: (text: string, isFinal: boolean) => void,
    onError: (err: string) => void,
    onEnd: () => void,
  ): boolean {
    if (!this.recognition) {
      onError("Speech recognition is not supported in this browser/environment.");
      return false;
    }

    if (this.isListening) {
      return true;
    }

    try {
      this.playActivationChime();
      this.isListening = true;

      this.recognition.onresult = (event: any) => {
        let interim = "";
        let final = "";

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            final += event.results[i][0].transcript;
          } else {
            interim += event.results[i][0].transcript;
          }
        }

        if (final) {
          onResult(final.trim(), true);
        } else if (interim) {
          onResult(interim.trim(), false);
        }
      };

      this.recognition.onerror = (event: any) => {
        this.isListening = false;
        onError(event.error === "no-speech" ? "No speech detected. Please try again." : `Microphone error: ${event.error}`);
      };

      this.recognition.onend = () => {
        this.isListening = false;
        onEnd();
      };

      this.recognition.start();
      return true;
    } catch (err: any) {
      this.isListening = false;
      onError(err.message || "Failed to start speech recognition.");
      return false;
    }
  }

  // Stop listening
  public stopListening() {
    if (this.recognition && this.isListening) {
      try {
        this.recognition.stop();
        this.playDeactivationChime();
      } catch {
        // Ignore
      }
    }
    this.isListening = false;
  }

  // Speak text out loud using SpeechSynthesis
  public speak(
    text: string,
    options: {
      rate?: number;
      pitch?: number;
      onStart?: () => void;
      onEnd?: () => void;
    } = {},
  ): void {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) {
      return;
    }

    // Cancel current speaking
    window.speechSynthesis.cancel();

    // Clean markdown symbols for cleaner speech
    const cleanText = text
      .replace(/[*_#`~[\]]/g, "")
      .replace(/https?:\/\/\S+/g, "link")
      .trim();

    if (!cleanText) return;

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = options.rate ?? 1.05; // Slightly brisk, modern pace
    utterance.pitch = options.pitch ?? 1.0;

    // Pick best modern English voice if available
    const voices = window.speechSynthesis.getVoices();
    const preferredVoice =
      voices.find((v) => v.name.includes("Natural") || v.name.includes("Google") || v.name.includes("David") || v.name.includes("Zira")) ||
      voices.find((v) => v.lang.startsWith("en"));

    if (preferredVoice) {
      utterance.voice = preferredVoice;
    }

    utterance.onstart = () => {
      this.isSpeaking = true;
      options.onStart?.();
    };

    utterance.onend = () => {
      this.isSpeaking = false;
      options.onEnd?.();
    };

    utterance.onerror = () => {
      this.isSpeaking = false;
      options.onEnd?.();
    };

    window.speechSynthesis.speak(utterance);
  }

  public stopSpeaking(): void {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      this.isSpeaking = false;
    }
  }
}

export const voiceEngine = new VoiceEngine();
