# 🎤 Audio Echo Fix Guide

## ✅ What Was Fixed

Added audio processing constraints to `getUserMedia`:
- **echoCancellation**: Removes echo/feedback from speakers
- **noiseSuppression**: Reduces background noise
- **autoGainControl**: Automatically adjusts microphone volume

## 🔧 Restart Frontend

```bash
# Stop frontend (Ctrl+C)
# Then restart:
cd frontend
npm run dev
```

## 🎧 Recommended Setup

### Option 1: Headphones (Best)
✅ **Use headphones/earbuds** to completely eliminate echo
- Wired headphones work best
- Bluetooth works but may have slight delay

### Option 2: Mute Output During Recording
✅ **Lower or mute your computer speakers** during the interview
- You'll still hear the AI voice agent (optional)
- Or use a separate audio device for voice agent

### Option 3: Browser Audio Settings
Check your browser's audio settings:

**Chrome:**
1. Go to `chrome://settings/content/microphone`
2. Select your site
3. Ensure microphone permissions are set

**Firefox:**
1. Click the lock icon in address bar
2. Select "More Information"
3. Check microphone permissions

## 🐛 If Echo Still Persists

### Check These Settings:

1. **System Audio Settings**
   - Lower computer volume
   - Use headphones

2. **Browser Console**
   - Open DevTools (F12)
   - Check for audio constraint errors

3. **Microphone Volume**
   - Lower mic sensitivity in system settings
   - Don't place mic too close to speakers

4. **Voice Agent Volume**
   - The ElevenLabs voice agent might be too loud
   - Lower its volume if it's causing feedback

## 📝 Technical Details

The code now uses:
```typescript
audio: {
  echoCancellation: true,    // Filters out speaker audio from mic
  noiseSuppression: true,     // Reduces background noise
  autoGainControl: true       // Normalizes volume levels
}
```

These are **browser-level** audio processing features that work automatically.

---

**Status**: Ready to test! Restart frontend and try an interview.
