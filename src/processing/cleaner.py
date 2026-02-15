"""
PHASE 3: Clean Subtitles
Steps:
1. Read .vtt files from data/raw/subtitles/
2. Remove timestamps, tags, empty lines
3. Save clean text to data/processed/cleaned/
"""

import os
import re

INPUT_DIR = 'data/raw/subtitles'
OUTPUT_DIR = 'data/processed/cleaned'


def clean_vtt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    clean_lines = []
    
    for line in lines:
        line = line.strip()
        
        if not line:
            continue
        if line.startswith('WEBVTT'):
            continue
        if '-->' in line:
            continue
        if re.match(r'^\d+$', line):
            continue
        if line.startswith('<'):
            continue
        
        line = re.sub(r'<[^>]+>', '', line)
        
        if line:
            clean_lines.append(line)
    
    return ' '.join(clean_lines)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    vtt_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.vtt')]
    
    print(f"🧹 Cleaning {len(vtt_files)} subtitle files...")
    
    for i, filename in enumerate(vtt_files, 1):
        input_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename.replace('.vtt', '.txt'))
        
        clean_text = clean_vtt(input_path)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(clean_text)
        
        print(f"  ✅ {i}/{len(vtt_files)} - {filename}")
    
    print(f"\n✅ Cleaned {len(vtt_files)} files saved to {OUTPUT_DIR}")


if __name__ == '__main__':
    main()

