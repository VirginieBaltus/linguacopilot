"""
PHASE 7: Streamlit Dashboard for Flashcard Learning
Features:
- Select learning level
- Two modes: DE→FR and FR→DE
- Review flashcards with flip animation
- Track and persist progress in database
"""

import streamlit as st
import sqlite3
from datetime import datetime

DB_PATH = 'data/linguacopilot.db'

st.set_page_config(page_title="LinguaCopilot", page_icon="🇩🇪", layout="wide")


def get_flashcards(level):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT id, word, level, sentence_de, sentence_fr
    FROM flashcards
    WHERE level = ?
    ORDER BY RANDOM()
    """, (level,))
    
    flashcards = cursor.fetchall()
    conn.close()
    
    return flashcards


def get_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT level, COUNT(*) FROM flashcards GROUP BY level")
    stats = dict(cursor.fetchall())
    
    conn.close()
    
    return stats


def save_progress(word, correct):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if correct:
        cursor.execute("""
        INSERT INTO user_progress (word, correct_count, incorrect_count, last_seen)
        VALUES (?, 1, 0, ?)
        ON CONFLICT(word) DO UPDATE SET
            correct_count = correct_count + 1,
            last_seen = ?
        """, (word, datetime.now(), datetime.now()))
    else:
        cursor.execute("""
        INSERT INTO user_progress (word, correct_count, incorrect_count, last_seen)
        VALUES (?, 0, 1, ?)
        ON CONFLICT(word) DO UPDATE SET
            incorrect_count = incorrect_count + 1,
            last_seen = ?
        """, (word, datetime.now(), datetime.now()))
    
    conn.commit()
    conn.close()


def get_overall_progress():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT 
        SUM(correct_count) as total_correct,
        SUM(incorrect_count) as total_incorrect,
        COUNT(*) as words_practiced
    FROM user_progress
    """)
    
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0] is not None:
        return {
            'total_correct': result[0],
            'total_incorrect': result[1],
            'words_practiced': result[2]
        }
    return {'total_correct': 0, 'total_incorrect': 0, 'words_practiced': 0}


def main():
    st.title("🇩🇪 LinguaCopilot - German Flashcards")
    st.markdown("Learn German vocabulary with AI-generated example sentences!")
    
    stats = get_stats()
    overall_progress = get_overall_progress()
    
    st.sidebar.header("Settings")
    
    available_levels = list(stats.keys())
    selected_level = st.sidebar.selectbox(
        "Choose your level:",
        available_levels,
        index=available_levels.index('B2') if 'B2' in available_levels else 0
    )
    
    mode = st.sidebar.radio(
        "Learning mode:",
        ["🇩🇪 → 🇫🇷 German to French", "🇫🇷 → 🇩🇪 French to German"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Available Flashcards")
    for level, count in sorted(stats.items()):
        st.sidebar.write(f"{level}: {count} cards")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📈 Overall Progress")
    st.sidebar.metric("Words Practiced", overall_progress['words_practiced'])
    st.sidebar.metric("Total Correct", overall_progress['total_correct'])
    st.sidebar.metric("Total Incorrect", overall_progress['total_incorrect'])
    
    if overall_progress['total_correct'] + overall_progress['total_incorrect'] > 0:
        accuracy = (overall_progress['total_correct'] / 
                   (overall_progress['total_correct'] + overall_progress['total_incorrect'])) * 100
        st.sidebar.metric("Overall Accuracy", f"{accuracy:.1f}%")
    
    if 'flashcards' not in st.session_state or st.session_state.get('last_level') != selected_level:
        st.session_state.flashcards = get_flashcards(selected_level)
        st.session_state.last_level = selected_level
        st.session_state.current_index = 0
        st.session_state.show_answer = False
    
    if 'show_answer' not in st.session_state:
        st.session_state.show_answer = False
    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0
    
    flashcards = st.session_state.flashcards
    
    if not flashcards:
        st.warning(f"No flashcards available for level {selected_level}")
        return
    
    current_card = flashcards[st.session_state.current_index]
    card_id, word, level, sentence_de, sentence_fr = current_card
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"### Card {st.session_state.current_index + 1} / {len(flashcards)}")
        
        st.markdown(f"## 📝 Word: **{word}** ({level})")
        
        st.markdown("---")
        
        if "German to French" in mode:
            st.markdown(f"### 🇩🇪 German:")
            st.markdown(f"> {sentence_de}")
            
            if st.session_state.show_answer:
                st.markdown(f"### 🇫🇷 French:")
                st.markdown(f"> {sentence_fr}")
        else:
            st.markdown(f"### 🇫🇷 French:")
            st.markdown(f"> {sentence_fr}")
            
            if st.session_state.show_answer:
                st.markdown(f"### 🇩🇪 German:")
                st.markdown(f"> {sentence_de}")
        
        if not st.session_state.show_answer:
            if st.button("🔄 Show Translation", use_container_width=True, key="show_btn"):
                st.session_state.show_answer = True
                st.rerun()
        else:
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button("✅ I knew it!", use_container_width=True, key="correct_btn"):
                    save_progress(word, correct=True)
                    st.session_state.current_index = (st.session_state.current_index + 1) % len(flashcards)
                    st.session_state.show_answer = False
                    st.rerun()
            
            with col_b:
                if st.button("❌ I didn't know", use_container_width=True, key="wrong_btn"):
                    save_progress(word, correct=False)
                    st.session_state.current_index = (st.session_state.current_index + 1) % len(flashcards)
                    st.session_state.show_answer = False
                    st.rerun()


if __name__ == '__main__':
    main()