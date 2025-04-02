import streamlit as st
import ollama
import base64
import re

# Function to encode image as base64
def encode_image(image_file):
    img_bytes = image_file.read()
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    return img_base64

# Streamlit Page Configuration
st.set_page_config(
    page_title="Forensic Image Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title('🔍 Forensic Image Analyzer')
st.markdown("""
This tool analyzes images to detect objects **relevant to forensic crime investigation**.
- Upload an image, and the AI will identify **crime-related objects**.
- The AI will **ignore unrelated objects** and focus only on **forensic evidence**.
""")

# Sidebar Information
st.sidebar.header("About This Project")
st.sidebar.info("""
- *Developed with*: Streamlit and Ollama
- *Model*: LLaVA-Phi3
- *Features*: Forensic image recognition + AI
""")
st.sidebar.markdown("---")
st.sidebar.header("How to Use")
st.sidebar.markdown("""
1. Upload an image (JPG, JPEG, or PNG).
2. Click **Analyze Image**.
3. View **forensic-related objects** detected.
""")

if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# Display Chat Messages
def display_chat():
    st.markdown("### Forensic Analysis")
    for msg in st.session_state.messages:
        if msg['role'] == 'user':
            st.markdown(f"""
            <div style="text-align: right; background-color: #0078d4; color: white; padding: 10px; border-radius: 8px; margin-bottom: 10px;">
            <b>You:</b> {msg['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="text-align: left; background-color: #eaeaea; color: black; padding: 10px; border-radius: 8px; margin-bottom: 10px;">
            <b>Bot:</b> {msg['content']}
            </div>
            """, unsafe_allow_html=True)

display_chat()

st.markdown("### Upload Image for Analysis")
uploaded_image = st.file_uploader("📷 Upload an image", type=['jpg', 'jpeg', 'png'])

# List of forensic-relevant objects
forensic_objects = [
    "weapon", "gun", "knife", "blood", "fingerprint", "footprint", "bullet", "casing",
    "license plate", "vehicle", "glass shard", "money", "drugs", "handprint", "mask", 
    "gloves", "document", "wallet", "cellphone", "rope", "chains", "tape", "broken lock"
]

# Process Image with AI
if st.button("Analyze Image"):
    if uploaded_image:
        st.session_state.messages.append({'role': 'user', 'content': "Analyze this image for forensic evidence."})

        # Encode Image
        img_base64 = encode_image(uploaded_image)

        # AI Query with Focused Prompt
        query_prompt = """Analyze this image and identify only objects that are relevant to forensic crime investigation. 
        Focus only on items that could serve as clues or evidence, such as weapons, blood stains, fingerprints, footprints, 
        bullet casings, documents, vehicles, or any other crime-related object. Ignore any unrelated objects.
        Respond in a structured format listing the detected forensic objects and their significance.
        """

        response_text = ""
        bot_placeholder = st.empty()

        # AI Processing
        with st.spinner('Processing...'):
            stream = ollama.chat(
                model='llava-phi3',
                messages=[{'role': 'user', 'content': query_prompt, 'images': [img_base64]}],
                stream=True,
            )

            for chunk in stream:
                response_text += chunk['message']['content']
                bot_placeholder.markdown(f"""
                <div style="text-align: left; background-color: #eaeaea; color: black; padding: 10px; border-radius: 8px;">
                <b>Bot:</b> {response_text}
                </div>
                """, unsafe_allow_html=True)

        # Filter Response to Show Only Forensic Objects
        detected_objects = [obj for obj in forensic_objects if obj in response_text.lower()]
        
        if detected_objects:
            filtered_response = "**Detected Forensic Objects:**\n\n"
            for obj in detected_objects:
                filtered_response += f"- **{obj.capitalize()}**: This could be a potential piece of evidence.\n"
            st.success(filtered_response)
        else:
            st.warning("No forensic-relevant objects detected.")

        # Save bot response
        st.session_state.messages.append({'role': 'bot', 'content': response_text})

    else:
        st.warning("Please upload an image before analyzing.")

