import streamlit as st

def write():
    with open('README.md', 'r') as f:
        body = f.readlines()

    
    about = [body[0]]
    for line in body[21:-42]:
        about.append(line)
    about = ''.join(about)
    st.write(about)

    return None