import streamlit as st

def write():
    with open('README.md', 'r') as f:
        body = f.readlines()
    
    disclaimer = [body[1]]
    for line in body[2:3]:
        disclaimer.append(line)
    disclaimer = ''.join(disclaimer)
    st.write(disclaimer)

    return None