import streamlit as st
import boto3
import json
import os

# Page config
st.set_page_config(
    page_title="IndicVoices Audio Dashboard",
    page_icon="🎧",
    layout="wide"
)

# S3 Configuration - Use environment variables or Streamlit secrets
AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "indicvoices")

@st.cache_resource
def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )

@st.cache_data(ttl=300)
def list_languages(_s3_client):
    try:
        response = _s3_client.list_objects_v2(Bucket=BUCKET_NAME, Delimiter='/')
        languages = []
        if 'CommonPrefixes' in response:
            for prefix in response['CommonPrefixes']:
                lang = prefix['Prefix'].rstrip('/')
                languages.append(lang)
        return languages
    except Exception as e:
        st.error(f"Error: {e}")
        return []

@st.cache_data(ttl=300)
def list_samples(_s3_client, language):
    try:
        response = _s3_client.list_objects_v2(
            Bucket=BUCKET_NAME,
            Prefix=f"{language}/",
            Delimiter='/'
        )
        samples = []
        if 'CommonPrefixes' in response:
            for prefix in response['CommonPrefixes']:
                sample_id = prefix['Prefix'].split('/')[-2]
                samples.append(sample_id)
        return sorted(samples)
    except Exception as e:
        st.error(f"Error: {e}")
        return []

def get_metadata(s3_client, language, sample_id):
    try:
        key = f"{language}/{sample_id}/metadata.json"
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=key)
        return json.loads(response['Body'].read().decode('utf-8'))
    except:
        return None

def get_audio_url(s3_client, language, sample_id, filename):
    try:
        key = f"{language}/{sample_id}/{filename}"
        return s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': key},
            ExpiresIn=3600
        )
    except:
        return None

def main():
    st.title("🎧 IndicVoices Audio Dashboard")
    
    if not AWS_ACCESS_KEY or not AWS_SECRET_KEY:
        st.error("⚠️ AWS credentials not configured. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables.")
        return
    
    s3_client = get_s3_client()
    languages = list_languages(s3_client)
    
    if not languages:
        st.warning("No languages found.")
        return
    
    # Language selection
    col1, col2 = st.columns([1, 1])
    with col1:
        selected_language = st.selectbox("Select Language", languages, format_func=lambda x: x.title())
    
    samples = list_samples(s3_client, selected_language)
    
    if not samples:
        st.warning(f"No samples found for {selected_language}")
        return
    
    with col2:
        items_per_page = st.selectbox("Items per page", [10, 20, 50, 100], index=0)
    
    total_pages = (len(samples) + items_per_page - 1) // items_per_page
    
    # Initialize page in session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    
    # Top pagination
    st.markdown("---")
    top_cols = st.columns([1, 1, 1, 1, 1])
    with top_cols[0]:
        if st.button("⏮️ First", key="top_first"):
            st.session_state.current_page = 1
            st.rerun()
    with top_cols[1]:
        if st.button("◀️ Prev", key="top_prev"):
            if st.session_state.current_page > 1:
                st.session_state.current_page -= 1
                st.rerun()
    with top_cols[2]:
        st.markdown(f"**Page {st.session_state.current_page} of {total_pages}** ({len(samples)} samples)")
    with top_cols[3]:
        if st.button("Next ▶️", key="top_next"):
            if st.session_state.current_page < total_pages:
                st.session_state.current_page += 1
                st.rerun()
    with top_cols[4]:
        if st.button("Last ⏭️", key="top_last"):
            st.session_state.current_page = total_pages
            st.rerun()
    
    current_page = st.session_state.current_page
    start_idx = (current_page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, len(samples))
    page_samples = samples[start_idx:end_idx]
    
    # Table header
    st.markdown("---")
    header_cols = st.columns([1, 2, 2, 2, 2])
    header_cols[0].markdown("**Sample ID**")
    header_cols[1].markdown("**Verbatim Text**")
    header_cols[2].markdown("**Original Audio**")
    header_cols[3].markdown("**Denoised Audio**")
    header_cols[4].markdown("**Denoised + Normalized**")
    st.markdown("---")
    
    # Table rows
    for sample_id in page_samples:
        cols = st.columns([1, 2, 2, 2, 2])
        
        cols[0].markdown(f"`{sample_id}`")
        
        metadata = get_metadata(s3_client, selected_language, sample_id)
        verbatim = metadata.get('verbatim', 'N/A') if metadata else 'N/A'
        cols[1].markdown(f"{verbatim}")
        
        original_url = get_audio_url(s3_client, selected_language, sample_id, 'original.wav')
        if original_url:
            cols[2].audio(original_url)
        else:
            cols[2].markdown("❌")
        
        denoised_url = get_audio_url(s3_client, selected_language, sample_id, 'denoised.wav')
        if denoised_url:
            cols[3].audio(denoised_url)
        else:
            cols[3].markdown("❌")
        
        denoised_norm_url = get_audio_url(s3_client, selected_language, sample_id, 'denoised_normalized.wav')
        if denoised_norm_url:
            cols[4].audio(denoised_norm_url)
        else:
            cols[4].markdown("❌")
        
        st.markdown("---")
    
    # Bottom pagination
    st.markdown("")
    bottom_cols = st.columns([1, 1, 1, 1, 1])
    with bottom_cols[0]:
        if st.button("⏮️ First", key="bot_first"):
            st.session_state.current_page = 1
            st.rerun()
    with bottom_cols[1]:
        if st.button("◀️ Prev", key="bot_prev"):
            if st.session_state.current_page > 1:
                st.session_state.current_page -= 1
                st.rerun()
    with bottom_cols[2]:
        st.markdown(f"**Page {st.session_state.current_page} of {total_pages}**")
    with bottom_cols[3]:
        if st.button("Next ▶️", key="bot_next"):
            if st.session_state.current_page < total_pages:
                st.session_state.current_page += 1
                st.rerun()
    with bottom_cols[4]:
        if st.button("Last ⏭️", key="bot_last"):
            st.session_state.current_page = total_pages
            st.rerun()

if __name__ == "__main__":
    main()
