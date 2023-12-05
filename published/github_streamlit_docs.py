import streamlit as st
import base64
import os
import subprocess
import shutil
import stat

def on_rm_error(func, path, exc_info):
    """
    Error handler for shutil.rmtree.
    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.
    If the error is for another reason it re-raises the error.
    """
    if not os.access(path, os.W_OK):
        # Is the error an access error?
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise

def concatenate_md_files(repo_url):
    temp_dir = "temp_repo"
    with st.status("Cloning repository...") as status:
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, onerror=on_rm_error)

            subprocess.run(["git", "clone", repo_url, temp_dir], check=True)
            status.update(label="Concatenating markdown files...", state="running")

            concatenated_content = ""
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith(".md"):
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                            concatenated_content += f.read() + "\n\n"
            status.update(label="Markdown files concatenated successfully.", state="complete")
        except subprocess.CalledProcessError as e:
            status.update(label=f"Error cloning repository: {e}", state="error")
            return ""
        finally:
            shutil.rmtree(temp_dir, onerror=on_rm_error)

    return concatenated_content

# Function to convert the concatenated content to a downloadable file
def get_md_download_link(md_content, filename="concatenated_document.md"):
    b64 = base64.b64encode(md_content.encode()).decode()
    href = f'<a href="data:file/md;base64,{b64}" download="{filename}">Download concatenated document</a>'
    return href

# Streamlit app interface
st.title('GitHub Markdown Aggregator')
repo_url = st.text_input('Enter the GitHub Repository URL', '')

if st.button('Aggregate Markdown Files'):
    if repo_url:
        md_content = concatenate_md_files(repo_url)
        download_link = get_md_download_link(md_content)
        st.markdown(download_link, unsafe_allow_html=True)
        st.markdown(md_content, unsafe_allow_html=True)
    else:
        st.error('Please enter a valid GitHub Repository URL.')
