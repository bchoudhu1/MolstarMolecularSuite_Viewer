import streamlit as st
import tempfile

from streamlit_molstar import (
    st_molstar,
    st_molstar_rcsb,
    st_molstar_remote
)
from streamlit_molstar.auto import st_molstar_auto
from streamlit_molstar.pocket import get_pockets_from_local_protein
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
        "Trajectory Viewer",
        "Pocket Detection",
        "Docking Viewer",
        "Auto Viewer"
    ]
)

# =================================================
# 1️⃣ STRUCTURE VIEWER (No file upload)
# =================================================

if page == "Structure Viewer":

    st.header("🔎 Structure Viewer")

    mode = st.radio(
        "Select Input Type",
        ["RCSB ID", "Remote URL"]
    )

    if mode == "RCSB ID":
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


# =================================================
# 2️⃣ TRAJECTORY VIEWER (Correct Syntax)
# =================================================

elif page == "Trajectory Viewer":

    st.header("🎞️ Trajectory Viewer (PDB + XTC)")

    topology_file = st.file_uploader("Upload Topology (PDB)", type=["pdb"])
    xtc_file = st.file_uploader("Upload Trajectory (XTC)", type=["xtc"])

    if st.button("Load Trajectory"):

        if topology_file is None or xtc_file is None:
            st.warning("Please upload both PDB and XTC files.")
            st.stop()

        # Save PDB
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdb") as tmp_pdb:
            tmp_pdb.write(topology_file.getbuffer())
            pdb_path = tmp_pdb.name

        # Save XTC
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xtc") as tmp_xtc:
            tmp_xtc.write(xtc_file.getbuffer())
            xtc_path = tmp_xtc.name

        # ✅ CORRECT TRAJECTORY SYNTAX
        st_molstar(
            pdb_path,
            xtc_path,
            key="trajectory_view"
        )


# =================================================
# 3️⃣ POCKET DETECTION
# =================================================

elif page == "Pocket Detection":

    st.header("🎯 Pocket Detection (P2Rank)")

    p2rank_home = st.text_input("P2Rank Installation Path")

    protein_path = st.text_input("Local Protein Path")

    if st.button("Run Pocket Detection"):

        if not p2rank_home or not protein_path:
            st.warning("Provide both P2Rank path and protein path.")
            st.stop()

        pockets = get_pockets_from_local_protein(
            protein_path,
            p2rank_home=p2rank_home
        )

        st.subheader("Detected Pockets")

        for i, pocket in enumerate(pockets.values(), start=1):
            st.write(f"Pocket {i}")
            st.write(pocket)

        st_molstar(protein_path, key="pocket_view")


# =================================================
# 4️⃣ DOCKING VIEWER
# =================================================

elif page == "Docking Viewer":

    st.header("🔬 Docking Viewer")

    protein_upload = st.file_uploader("Upload Protein (PDB)", type=["pdb"])
    docking_upload = st.file_uploader("Upload Docked Ligand (SDF)", type=["sdf"])
    gt_upload = st.file_uploader("Upload Ground Truth Ligand (SDF)", type=["sdf"])

    if st.button("Run Docking Visualization"):

        if protein_upload is None or docking_upload is None or gt_upload is None:
            st.warning("Upload all three files.")
            st.stop()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdb") as tmp_prot:
            tmp_prot.write(protein_upload.getbuffer())
            protein_path = tmp_prot.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=".sdf") as tmp_dock:
            tmp_dock.write(docking_upload.getbuffer())
            docking_path = tmp_dock.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=".sdf") as tmp_gt:
            tmp_gt.write(gt_upload.getbuffer())
            gt_path = tmp_gt.name

        st_molstar_docking(
            protein_path,
            docking_path,
            gt_ligand_file_path=gt_path,
            key="docking_view"
        )


# =================================================
# 5️⃣ AUTO VIEWER
# =================================================

elif page == "Auto Viewer":

    st.header("⚡ Auto File Viewer")

    auto_mode = st.radio(
        "Select Source",
        ["Remote URLs", "Local Files"]
    )

    if auto_mode == "Remote URLs":

        urls = st.text_area(
            "Enter URLs (one per line)",
            """https://files.rcsb.org/download/1LOL.pdb
https://files.rcsb.org/download/3PTB.pdb"""
        )

        if st.button("Load Remote Structures"):

            files = [u.strip() for u in urls.split("\n") if u.strip()]

            if not files:
                st.warning("Enter at least one URL.")
                st.stop()

            st_molstar_auto(files, key="auto_remote_view")

    elif auto_mode == "Local Files":

        uploaded_files = st.file_uploader(
            "Upload Multiple Files",
            accept_multiple_files=True
        )

        if st.button("Load Local Files"):

            if not uploaded_files:
                st.warning("Upload at least one file.")
                st.stop()

            file_paths = []

            for file in uploaded_files:
                suffix = "." + file.name.split(".")[-1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(file.getbuffer())
                    file_paths.append(tmp.name)

            st_molstar_auto(file_paths, key="auto_local_view")

