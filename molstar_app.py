import streamlit as st
from streamlit_molstar import (
    st_molstar,
    st_molstar_rcsb,
    st_molstar_remote
)
from streamlit_molstar.auto import st_molstar_auto
from streamlit_molstar.pocket import (
    select_pocket_from_local_protein,
    select_pocket_from_upload_protein
)
from streamlit_molstar.docking import st_molstar_docking


# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(layout="wide", page_title="Mol* Molecular Suite")

st.title("🧬 Mol* Molecular Visualization Suite")

# -------------------------------------------------
# SIDEBAR NAVIGATION
# -------------------------------------------------
page = st.sidebar.radio(
    "Select Module",
    [
        "Structure Viewer",
        "Pocket Selection",
        "Docking Viewer",
        "Auto Viewer"
    ]
)

# -------------------------------------------------
# 1️⃣ STRUCTURE VIEWER
# -------------------------------------------------
if page == "Structure Viewer":

    st.header("🔎 Structure Viewer")

    mode = st.radio(
        "Select Input Type",
        ["Local File", "RCSB ID", "Remote URL", "Trajectory (PDB + XTC)"]
    )

    if mode == "Local File":
        uploaded = st.file_uploader("Upload PDB/CIF file")
        if uploaded:
            st_molstar(uploaded, key="local_structure")

    elif mode == "RCSB ID":
        pdb_id = st.text_input("Enter RCSB PDB ID", "1LOL")
        if pdb_id:
            st_molstar_rcsb(pdb_id, key="rcsb_structure")

    elif mode == "Remote URL":
        url = st.text_input(
            "Enter Remote Structure URL",
            "https://files.rcsb.org/view/1LOL.cif"
        )
        if url:
            st_molstar_remote(url, key="remote_structure")

    elif mode == "Trajectory (PDB + XTC)":
        st.write("Upload Structure + Trajectory")
        pdb_file = st.file_uploader("Upload PDB", type=["pdb"])
        xtc_file = st.file_uploader("Upload XTC", type=["xtc"])

        if pdb_file and xtc_file:
            st_molstar(pdb_file, xtc_file, key="trajectory_view")


# -------------------------------------------------
# 2️⃣ POCKET SELECTION
# -------------------------------------------------
elif page == "Pocket Selection":

    st.header("🎯 Pocket Detection (P2Rank)")

    pocket_mode = st.radio(
        "Select Mode",
        ["Local Protein", "Upload Protein"]
    )

    prank_home = st.text_input(
        "P2Rank Installation Path",
        "/Users/your_user/p2rank_2.4/"
    )

    if pocket_mode == "Local Protein":
        protein_path = st.text_input(
            "Local Protein Path",
            "examples/pocket/protein.pdb"
        )

        if protein_path:
            selected = select_pocket_from_local_protein(
                protein_path,
                prank_home=prank_home
            )

            if selected:
                protein_file_path, pocket = selected
                st.success("Pocket Selected!")
                st.write("Protein Path:", protein_file_path)
                st.write("Selected Pocket:", pocket)

    elif pocket_mode == "Upload Protein":

        selected = select_pocket_from_upload_protein(
            prank_home=prank_home
        )

        if selected:
            protein_file_path, pocket = selected
            st.success("Pocket Selected!")
            st.write("Protein Path:", protein_file_path)
            st.write("Selected Pocket:", pocket)


# -------------------------------------------------
# 3️⃣ DOCKING VIEWER
# -------------------------------------------------
elif page == "Docking Viewer":

    st.header("🔬 Docking Visualization")

    protein_file = st.text_input(
        "Protein File Path",
        "examples/docking/2zy1_protein.pdb"
    )

    docking_file = st.text_input(
        "Docked Ligand File (SDF)",
        "examples/docking/docking.2zy1.0.sdf"
    )

    gt_file = st.text_input(
        "Ground Truth Ligand (SDF)",
        "examples/docking/2zy1_ligand.sdf"
    )

    height = st.slider("Viewer Height", 200, 800, 400)

    if protein_file and docking_file:
        st_molstar_docking(
            protein_file,
            docking_file,
            gt_ligand_file_path=gt_file,
            key="docking_view",
            height=height
        )


# -------------------------------------------------
# 4️⃣ AUTO VIEWER
# -------------------------------------------------
elif page == "Auto Viewer":

    st.header("⚡ Auto File Viewer")

    auto_mode = st.radio(
        "Select Source",
        ["Remote URLs", "Local Files"]
    )

    height = st.slider("Viewer Height", 200, 800, 320)

    if auto_mode == "Remote URLs":
        urls = st.text_area(
            "Enter URLs (one per line)",
            "https://files.rcsb.org/download/3PTB.pdb\nhttps://files.rcsb.org/download/1LOL.pdb"
        )

        files = [u.strip() for u in urls.split("\n") if u.strip()]
        if files:
            st_molstar_auto(files, key="auto_remote", height=f"{height}px")

    elif auto_mode == "Local Files":
        uploaded_files = st.file_uploader(
            "Upload Multiple Files",
            accept_multiple_files=True
        )

        if uploaded_files:
            st_molstar_auto(uploaded_files, key="auto_local", height=f"{height}px")

