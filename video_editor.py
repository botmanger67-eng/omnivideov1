from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips, afx
import tempfile
import numpy as np

async def render_video(video_paths: list, voiceover_path: str, music_path: str, 
                       target_duration: float, output_filename: str = "final_video.mp4") -> str:
    """
    Combine video clips, overlay voiceover, and add background music.
    Returns the path to the rendered MP4.
    """
    # 1. Load and prepare video clips
    clips = []
    for vpath in video_paths:
        clip = VideoFileClip(vpath)
        clips.append(clip)
    
    # If total duration of clips is less than target, loop last clip
    total_duration = sum(c.duration for c in clips)
    if total_duration < target_duration:
        last_clip = clips[-1]
        loops_needed = int(np.ceil((target_duration - total_duration) / last_clip.duration))
        extra = [last_clip.copy() for _ in range(loops_needed)]
        clips.extend(extra)
    
    # Trim/concatenate to exactly target_duration
    final_clip = concatenate_videoclips(clips).subclip(0, target_duration)
    
    # 2. Load voiceover audio
    voiceover = AudioFileClip(voiceover_path)
    # If voiceover is shorter than target, pad silence; if longer, trim
    if voiceover.duration < target_duration:
        silence = afx.audio_loop(voiceover, duration=target_duration)  # simple pad
        voiceover = silence
    else:
        voiceover = voiceover.subclip(0, target_duration)
    
    # 3. Load background music, lower volume, loop to fit
    music = AudioFileClip(music_path)
    music = music.volumex(0.25)  # reduce volume to 25%
    if music.duration < target_duration:
        music = afx.audio_loop(music, duration=target_duration)
    else:
        music = music.subclip(0, target_duration)
    
    # 4. Mix voiceover and background music
    final_audio = CompositeAudioClip([voiceover, music])
    final_clip = final_clip.set_audio(final_audio)
    
    # 5. Write output
    out_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
    final_clip.write_videofile(out_path, codec="libx264", audio_codec="aac", fps=24, verbose=False, logger=None)
    
    # Cleanup temporary clips
    for c in clips:
        c.close()
    voiceover.close()
    music.close()
    final_clip.close()
    
    return out_path

from moviepy.audio.compositing import CompositeAudioClip  # needed for mixing