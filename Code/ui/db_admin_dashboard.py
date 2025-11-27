import streamlit as st
import os
import json
from pathlib import Path
import chromadb
from chromadb.config import Settings

# Always resolve paths relative to the Code directory
CODE_DIR = Path(__file__).parent.parent.resolve()

st.set_page_config(page_title="DB Admin Dashboard", layout="wide")
st.title("🗄️ DB Admin Dashboard")

# --- Helper functions ---
def list_files(folder, exts=None):
    files = []
    for root, _, filenames in os.walk(folder):
        for f in filenames:
            if not exts or any(f.lower().endswith(e) for e in exts):
                files.append(os.path.join(root, f))
    return files

def read_json_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}

def read_md_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error: {e}"

def write_md_file(path, content):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        return False

def list_dir(path):
    return [f for f in os.listdir(path) if not f.startswith('.')]

# --- Sidebar navigation ---
section = st.sidebar.radio("Select Section", [
    "ChromaDB",
    "TinyDB",
    "Workflow State",
    "Docs (Markdown)"
])

# --- ChromaDB ---
if section == "ChromaDB":
    st.header("ChromaDB Collections")
    chroma_db_path = str(CODE_DIR / "chroma_db")
    if not os.path.exists(chroma_db_path):
        st.warning(f"ChromaDB path not found: {chroma_db_path}")
    else:
        # List all collections
        chroma_client = chromadb.PersistentClient(
            path=chroma_db_path,
            settings=Settings(anonymized_telemetry=False, allow_reset=True)
        )
        collections = chroma_client.list_collections()
        col_names = [c.name for c in collections]
        if not col_names:
            st.info("No collections found in ChromaDB.")
        else:
            selected_col = st.selectbox("Select a collection", col_names)
            collection = chroma_client.get_collection(selected_col)
            # Show document count
            st.write(f"Collection: {selected_col}")
            st.write(f"Document count: {collection.count()}")
            # List documents (show first 20)
            docs = collection.get(limit=20)
            ids = docs.get('ids', [])
            documents = docs.get('documents', [])
            metadatas = docs.get('metadatas', [])
            if ids:
                st.write(f"Showing first {len(ids)} documents:")
                for i, (doc_id, doc, meta) in enumerate(zip(ids, documents, metadatas)):
                    with st.expander(f"Doc {i+1} - ID: {doc_id}"):
                        st.write("**Text:**", doc)
                        st.write("**Metadata:**", meta)
                        if st.button(f"Delete Document {doc_id}", key=f"del_{doc_id}"):
                            collection.delete(ids=[doc_id])
                            st.success(f"Deleted document {doc_id}")
                            st.experimental_rerun()
            else:
                st.info("No documents in this collection.")

# --- TinyDB ---
elif section == "TinyDB":
    st.header("TinyDB Audit/Logs")
    tinydb_dir = str(CODE_DIR / "audit_logs")
    if not os.path.exists(tinydb_dir):
        st.warning(f"TinyDB dir not found: {tinydb_dir}")
    else:
        json_files = list_files(tinydb_dir, exts=[".json"])
        file = st.selectbox("Select a TinyDB JSON file", json_files)
        if file:
            data = read_json_file(file)
            st.json(data)
        if st.button("Delete Selected File"):
            os.remove(file)
            st.success(f"Deleted {file}")

# --- Workflow State ---
elif section == "Workflow State":
    st.header("Workflow State Files")
    wf_dir = str(CODE_DIR / "workflow_state")
    if not os.path.exists(wf_dir):
        st.warning(f"Workflow state dir not found: {wf_dir}")
    else:
        files = list_files(wf_dir, exts=[".json"])
        file = st.selectbox("Select a workflow state file", files)
        if file:
            data = read_json_file(file)
            st.json(data)
        if st.button("Delete Selected File"):
            os.remove(file)
            st.success(f"Deleted {file}")

# --- Docs (Markdown) ---
else:
    st.header("Docs (Markdown)")
    docs_dir = str(CODE_DIR / "docs")
    if not os.path.exists(docs_dir):
        st.warning(f"Docs dir not found: {docs_dir}")
    else:
        md_files = list_files(docs_dir, exts=[".md"])
        file = st.selectbox("Select a Markdown file", md_files)
        if file:
            content = read_md_file(file)
            st.markdown(f"### {os.path.basename(file)}")
            edited = st.text_area("Edit Markdown Content", value=content, height=400, key="md_edit")
            if st.button("Save Changes"):
                ok = write_md_file(file, edited)
                if ok:
                    st.success("File updated!")
                else:
                    st.error("Failed to update file.")
            st.code(edited, language="markdown")
