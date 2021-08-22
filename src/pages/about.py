import streamlit as st

def write():
    with open('README.md', 'r') as f:
        body = ''.join(f.readlines())

    st.write(body)
    
    return None