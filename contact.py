import streamlit as st
import os
import pathlib
import platform

def debug_paths():
    """
    Helper function to debug file path issues in Streamlit Cloud
    Add this to your app to troubleshoot deployment problems
    """
    
    st.subheader("🛠️ Path Debugging Information")
    
    # System information
    st.write("### System Info")
    system_info = {
        "Operating System": platform.system(),
        "Platform": platform.platform(),
        "Python Version": platform.python_version(),
        "Current Working Directory": os.getcwd(),
        "Script Location": pathlib.Path(__file__).parent.absolute()
    }
    
    for key, value in system_info.items():
        st.code(f"{key}: {value}")
    
    # Directory contents
    st.write("### Directory Contents")
    
    # Current directory
    try:
        st.write("**Current directory files:**")
        files = os.listdir('.')
        if files:
            st.code('\n'.join(files))
        else:
            st.code("No files found")
    except Exception as e:
        st.error(f"Error listing current directory: {e}")
    
    # Image directory
    try:
        image_dir = "image"
        st.write(f"**'{image_dir}' directory files:**")
        if os.path.exists(image_dir):
            files = os.listdir(image_dir)
            if files:
                st.code('\n'.join(files))
            else:
                st.code("Directory exists but is empty")
        else:
            st.error(f"Directory '{image_dir}' not found!")
            
            # Try alternate capitalization
            alt_image_dir = "Image"
            if os.path.exists(alt_image_dir):
                st.warning(f"However, '{alt_image_dir}' directory exists (case sensitive)!")
                st.code('\n'.join(os.listdir(alt_image_dir)))
    except Exception as e:
        st.error(f"Error listing image directory: {e}")
    
    # Parent directory
    try:
        parent_dir = os.path.dirname(os.getcwd())
        st.write(f"**Parent directory files:**")
        parent_files = os.listdir(parent_dir)
        if parent_files:
            st.code('\n'.join(parent_files[:20]))
            if len(parent_files) > 20:
                st.caption(f"...and {len(parent_files) - 20} more files")
        else:
            st.code("No files found in parent directory")
    except Exception as e:
        st.error(f"Error listing parent directory: {e}")
    
    # Test path resolution
    st.write("### Path Resolution Test")
    test_paths = [
        "image/om.png",
        "image\\om.png",  # Windows style
        os.path.join("image", "om.png"),
        os.path.join(os.getcwd(), "image", "om.png"),
        str(pathlib.Path(__file__).parent.absolute() / "image" / "om.png")
    ]
    
    for path in test_paths:
        exists = os.path.exists(path)
        st.code(f"Path: {path}\nExists: {exists}")

# Usage example - add this to a debug page or temporarily to your main app
if __name__ == "__main__":
    st.title("Streamlit Deployment Debugger")
    debug_paths()