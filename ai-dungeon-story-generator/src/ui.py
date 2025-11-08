"""
Streamlit UI helpers with CSS injection for a polished look.
Minimal, safe CSS included. For advanced UI, consider a React frontend.
"""
from typing import Optional
import streamlit as st


def inject_css():
    """
    Inject minimal CSS into the Streamlit app for a dark-themed look
    and polished spacing for story cards.
    """
    st.markdown(
        """
        <style>
        /* App-wide background and text colors */
        .stApp { 
            background-color: #0f1724; 
            color: #e6eef8; 
        }

        /* Adjust default container padding */
        .block-container {
            padding: 1.5rem 2rem;
        }

        /* Story card styling */
        .story-card {
            background: linear-gradient(
                180deg,
                rgba(255,255,255,0.02), 
                rgba(255,255,255,0.01)
            );
            padding: 16px; 
            border-radius: 12px; 
            margin-bottom: 12px;
        }

        /* Small muted text style */
        .small-muted {
            color: #9aa4b2;
            font-size: 12px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def story_card(title: str, body: str, uid: Optional[str] = None, muted_text: Optional[str] = None):
    """
    Display a story card with optional small muted text.
    
    Args:
        title (str): Title of the story.
        body (str): Story content.
        uid (Optional[str]): Optional unique ID for the card (for linking or JS hooks).
        muted_text (Optional[str]): Optional small muted text to display below the body.
    """
    html = f"<div class='story-card'><strong>{title}</strong>"
    html += f"<div style='margin-top:8px'>{body}</div>"

    if muted_text:
        html += f"<div class='small-muted' style='margin-top:4px'>{muted_text}</div>"

    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)
