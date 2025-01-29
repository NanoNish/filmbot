import streamlit as st
from PIL import Image
from api_client import (
    generate_ai_script,
    modify_uploaded_script,
    modify_script,
    generate_character_image,
    generate_shot_images,
)
from data_models import Shot, Shots, Script
from io import BytesIO
import random

if "shots" not in st.session_state:
    st.session_state.shots = []
if "script" not in st.session_state:
    st.session_state.script = ""

# Variables for upload script
st.session_state.uploaded_script = None
st.session_state.org_uploaded_script = ""

# Variables for generate script
st.session_state.script_prompt = ""
st.session_state.additional_prompt = ""
st.session_state.genres = None
st.session_state.generated_scipt = None

# Variables for main chars
# st.session_state.main_characters_gen = False

# Variables for storyboard
st.session_state.shots = []


st.sidebar.title("Navigation")
app_mode = st.sidebar.selectbox(
    "Choose an App",
    [
        "Upload Script",
        "Script Generation",
        "Modify Script",
        "Main Characters",
        "Storyboard Viewer",
    ],
)


def generate_shots(script):
    for i in range(len(script.shots)):
        shot = script.shots[i]
        shot.thumbnails = generate_shot_images(shot, script.main_characters)
        script.shots[i] = shot
    return script


def generate_chars(script):
    for i in range(len(script.main_characters)):
        char = script.main_characters[i]
        char.photo = generate_character_image(char.dressing_style, char.background)
        script.main_characters[i] = char
    return script


if app_mode == "Upload Script":
    st.title("Upload Script")
    uploaded_script = st.text_area(
        "Paste Script Here:", placeholder="Paste an existing script..."
    )

    col1, col2 = st.columns(2)
    with col1:
        continue_button = st.button("Continue")
    with col2:
        generate_button = st.button("Generate Using AI")

    if generate_button:
        # TODO: fox nav
        app_mode = "Script Generation"

    if continue_button and uploaded_script:
        # TODO: call API to format it
        st.session_state.org_uploaded_script = uploaded_script
        st.session_state.script = modify_uploaded_script(uploaded_script)
        st.text_area("Uploaded Script:", value=st.session_state.script, height=300)
        st.success("Script saved successfully!")

    elif continue_button:
        st.warning("Please enter a prompt to generate the script.")


elif app_mode == "Script Generation":
    st.title("Script Generation Tool")

    st.subheader("Enter Script Details")
    st.session_state.prompt = st.text_input(
        "Prompt:", placeholder="Enter a brief film prompt..."
    )
    st.session_state.additional_prompt = st.text_area(
        "Additional Details:", placeholder="Provide any extra context..."
    )
    st.session_state.genres = st.multiselect(
        "Select Genre:", ["Cinematic", "3D Cartoon", "Anime", "Scribble", "Film Noir"]
    )

    if st.button("Generate Script"):
        if st.session_state.prompt != "":
            # TODO: update script
            generated_script = generate_ai_script(
                st.session_state.prompt,
                st.session_state.additional_prompt,
                st.session_state.genres,
            )
            st.session_state.script = generated_script
            st.text_area("Generated Script:", value=generated_script, height=300)
        else:
            st.warning("Please enter a prompt to generate the script.")

elif app_mode == "Modify Script":
    st.title("Modify the Script")
    st.text_area("Original Script:", value=st.session_state.script, height=300)
    if feedback := st.chat_input("Add feedback"):
        st.session_state.script = modify_script(st.session_state.script, feedback)
        st.text_area("Script:", value=st.session_state.script, height=300)

elif app_mode == "Main Characters":
    st.title("Generate Main Characters")

    if st.button("Generate"):
        script = generate_chars(st.session_state.script)
        st.session_state.script = script
        st.session_state.main_characteres = script.main_characters
        st.session_state.main_characters_gen = True

    # Display Shots if Available
    if "main_characters_gen" in st.session_state:
        chars = st.session_state.script.main_characters
        rows = [
            chars[i : i + 4] for i in range(0, len(chars), 4)
        ]  # Grouping shots into rows of 4

        for row in rows:
            cols = st.columns(4)
            for col, char in zip(cols, row):
                with col:
                    if st.button("Expand", key=f"expand_{char.name}"):
                        st.session_state.selected_char = char
                    st.image(
                        char.photo,
                        caption=char.name,
                        use_container_width=True,
                    )

    # Modal Dialog for Expanded View
    if "selected_char" in st.session_state:
        char = st.session_state.selected_char
        with st.expander(f"Expanded View: {char.name}", expanded=True):
            st.image(char.photo)
            char.dressing_style = st.text_area(
                f"**Dressing Style:**", value=char.dressing_style
            )
            char.background = st.text_area(f"**Background:**", value=char.background)

            if st.button("Regenerate"):
                char.photo = generate_character_image(
                    char.dressing_style, char.background
                )

            # Close Button
            if st.button("Close Expanded View"):
                del st.session_state.selected_char

elif app_mode == "Storyboard Viewer":
    st.title("Generate and View Film Shots")

    # Generate Shots Button
    if st.button("Generate"):
        script = generate_shots(st.session_state.script)
        st.session_state.script = script
        st.session_state.storyboard = script.shots
        st.session_state.shots_gen = True

    # Display Shots if Available
    if "shots_gen" in st.session_state:
        shots = st.session_state.storyboard
        rows = [
            shots[i : i + 4] for i in range(0, len(shots), 4)
        ]  # Grouping shots into rows of 4

        for row in rows:
            cols = st.columns(4)
            for col, shot in zip(cols, row):
                with col:
                    if st.button("Expand", key=f"expand_{shot.description}"):
                        st.session_state.selected_shot = shot
                    st.image(
                        shot.thumbnails[0],
                        caption=shot.description,
                        use_container_width=True,
                    )

    # Modal Dialog for Expanded View
    if "selected_shot" in st.session_state:
        shot = st.session_state.selected_shot
        with st.expander(f"Expanded View:", expanded=True):
            st.text(shot.description)
            # st.image(shot.thumbnails[0], caption="Expanded Thumbnail")
            for img in shot.thumbnails:
                st.image(img)
            # st.markdown(f"**Long Description:** {shot['long_description']}")
            shot.camera_action = st.text_area(
                f"**Camera Movement:**", value=shot.camera_action
            )
            shot.action = st.text_area(f"**Action:**", value=shot.action)
            shot.dialogues = st.text_area(f"**Dialogues:**", value=shot.dialogues)

            if st.button("Regenerate"):
                shot.thumbnails = generate_shot_images(
                    shot, st.session_state.script.main_characters
                )

            # Close Button
            if st.button("Close Expanded View"):
                del st.session_state.selected_shot
