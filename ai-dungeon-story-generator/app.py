"""
Main Streamlit application entrypoint for AI Dungeon Story Generator.
Run: streamlit run app.py
"""
import os
from dotenv import load_dotenv
import streamlit as st
from src.model_loader import load_local_pipeline, HostedInference
from src.prompts import build_prompt
from src.story_generator import generate_variations
from src.story_moderation import simple_moderation_check

from src.utils import save_story_file, read_config
from src.ui import inject_css, story_card

# Load environment variables
load_dotenv()

# --- App config & page setup
st.set_page_config(
    page_title="AI Dungeon — Story Generator",
    layout="wide",
    initial_sidebar_state="expanded"
)
inject_css()

# Load configuration
CONFIG_PATH = os.path.join("config", "config.yaml")
config, has_cfg = read_config(CONFIG_PATH)
DEFAULT_MODEL = config.get("default_model", "gpt2-medium")
GENRES = config.get(
    "genres",
    ["Fantasy", "Mystery", "Sci-Fi", "Horror", "Open-ended"]
)

# --- Main title & description
st.title("AI Dungeon — Story Generator")
st.markdown(
    "Create cinematic, interactive story continuations using a local "
    "Hugging Face model or hosted inference."
)

# --- Sidebar controls
with st.sidebar:
    st.header("Settings")
    model_choice = st.selectbox(
        "Model",
        options=[DEFAULT_MODEL, "gpt2", "gpt2-medium", "gpt2-large", "EleutherAI/gpt-neo-1.3B"],
        index=0
    )
    use_hosted = st.checkbox(
        "Use Hosted Inference (Hugging Face)",
        value=False
    )
    if use_hosted:
        st.info("Hosted inference requires HUGGINGFACE_API_TOKEN in environment variables.")

    max_new_tokens = st.slider(
        "Max new tokens",
        min_value=50,
        max_value=1024,
        value=int(config.get("max_new_tokens", 300)),
        step=10
    )
    temperature = st.slider(
        "Temperature",
        min_value=0.1,
        max_value=1.5,
        value=float(config.get("temperature", 0.9)),
        step=0.05
    )
    top_p = st.slider(
        "Top-p",
        min_value=0.1,
        max_value=1.0,
        value=float(config.get("top_p", 0.9)),
        step=0.05
    )
    num_return = st.slider(
        "Number of continuations",
        min_value=1,
        max_value=6,
        value=int(config.get("num_return_sequences", 3))
    )
    repetition_penalty = st.slider(
        "Repetition penalty",
        min_value=1.0,
        max_value=2.5,
        value=float(config.get("repetition_penalty", 1.1)),
        step=0.1
    )
    seed_control = st.checkbox("Set seed for reproducibility", value=False)
    seed_val = None
    if seed_control:
        seed_val = st.number_input("Seed value", min_value=0, value=42, step=1)

# --- Input panel
col1, col2 = st.columns([3, 1])
with col1:
    st.subheader("Write your scene / prompt")
    prompt = st.text_area(
        "Prompt",
        height=200,
        placeholder="A rain-soaked village at dusk, witches' lanterns flicker in the marketplace..."
    )
    advanced = st.expander("Advanced prompt tips")
    with advanced:
        st.markdown(
            "- Include 2–3 character names\n"
            "- Mention a small conflict or objective\n"
            "- Choose tone (dark, whimsical, humorous)"
        )

with col2:
    st.subheader("Controls")
    genre = st.selectbox("Genre", options=GENRES)
    generate = st.button("Generate")

# --- Quick actions
st.markdown("---")
st.markdown("**Quick actions**")
if st.button("Clear saved outputs"):
    if 'outputs' in st.session_state:
        del st.session_state['outputs']
    st.success("Cleared outputs")

# --- Load pipeline or hosted client
if 'pipe' not in st.session_state or \
   st.session_state.get('model_name') != model_choice or \
   st.session_state.get('use_hosted') != use_hosted:

    try:
        if use_hosted:
            hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
            if not hf_token:
                st.warning("HUGGINGFACE_API_TOKEN not found in environment. Hosted inference disabled.")
                hosted_client = None
            else:
                hosted_client = HostedInference(hf_token)
            st.session_state['hosted_client'] = hosted_client
            st.session_state['model_type'] = 'hosted'

        else:
            with st.spinner(f"Loading {model_choice} (this may take a while)..."):
                pipe = load_local_pipeline(model_choice)
            st.session_state['pipe'] = pipe
            st.session_state['model_type'] = 'local'

        st.session_state['model_name'] = model_choice
        st.session_state['use_hosted'] = use_hosted

    except Exception as e:
        st.error(f"Model load failed: {e}")

# --- Generation
if generate:
    if not prompt or len(prompt.strip()) < 10:
        st.warning("Please write a prompt of at least ~10 characters.")
    else:
        assembled = build_prompt(prompt, genre)
        st.info("Generating. This may take a moment for larger models.")

        model_type = st.session_state.get('model_type', 'local')
        pipe_or_client = st.session_state.get('pipe') if model_type == 'local' else st.session_state.get('hosted_client')

        try:
            outputs = generate_variations(
                pipe_or_client,
                model_type=model_type,
                model_name=model_choice,
                prompt=assembled,
                n_return=num_return,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                repetition_penalty=repetition_penalty,
                seed=seed_val if seed_control else None,
            )
            st.session_state['outputs'] = outputs

        except Exception as e:
            st.error(f"Generation failed: {e}")

# --- Display outputs
if 'outputs' in st.session_state:
    st.markdown("---")
    st.subheader("Continuations")
    for out in st.session_state['outputs']:
        with st.container():
            title = f"Continuation #{out['id']}"
            story_card(title, out['continuation'])

            cols = st.columns([1, 1, 1, 4])
            if cols[0].button("Save", key=f"save_{out['id']}"):
                path = save_story_file(prompt, out['continuation'], genre)
                cols[0].success("Saved")
                cols[0].markdown(f"[Download]({path})")

            if cols[1].button("Append to prompt", key=f"append_{out['id']}"):
                st.session_state['prompt_appended'] = prompt + "\n\n" + out['continuation']
                st.experimental_rerun()

            if cols[2].button("Flag", key=f"flag_{out['id']}"):
                st.warning("Flagged for review")

            cols[3].markdown(f"**Generation params:** temp={temperature}, top_p={top_p}, tokens={max_new_tokens}")

# --- If prompt appended, show it
if 'prompt_appended' in st.session_state:
    st.success("Appended continuation to prompt")
    st.text_area("Updated prompt", value=st.session_state.pop('prompt_appended'), height=160)

# --- Simple moderation panel
st.markdown("---")
st.subheader("Moderation & logs")
moderation_enabled = config.get('moderation', {}).get('enabled', True)
if moderation_enabled and 'outputs' in st.session_state:
    for out in st.session_state['outputs']:
        hits = simple_moderation_check(out['continuation'], config.get('moderation', {}).get('banned_words'))
        if hits:
            st.error(f"Moderation hits in continuation #{out['id']}: {', '.join(hits)}")

st.markdown("---")
st.caption(
    "Built by a senior AI/ML engineering pattern. For production-grade deployment, "
    "add authentication, DB storage for user stories, and external moderation service."
)
