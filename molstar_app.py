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
        "Pocket Detection",
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
        uploaded = st.file_uploader("Upload PDB/CIF file", key="struct_local")
        if uploaded is not None:
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
        pdb_file = st.file_uploader("Upload PDB", type=["pdb"], key="traj_pdb")
        xtc_file = st.file_uploader("Upload XTC", type=["xtc"], key="traj_xtc")

        if pdb_file is not None and xtc_file is not None:
            st_molstar(pdb_file, xtc_file, key="trajectory_view")


# -------------------------------------------------
# 2️⃣ POCKET DETECTION
# -------------------------------------------------

elif page == "Pocket Detection":

    st.header("🎯 Pocket Detection (P2Rank)")

    p2rank_home = st.text_input(
        "P2Rank Installation Path",
        "/Users/bedabratachoudhury/Desktop/p2rank"
    )

    pocket_mode = st.radio(
        "Select Mode",
        ["Local Protein", "Upload Protein"]
    )

    # Session state init
    if "pockets" not in st.session_state:
        st.session_state.pockets = None

    if "protein_path" not in st.session_state:
        st.session_state.protein_path = None


    # -------- LOCAL MODE --------

    if pocket_mode == "Local Protein":

        protein_path = st.text_input("Local Protein Path")

        if st.button("Run Pocket Detection"):

            if not p2rank_home or not protein_path:
                st.warning("Provide P2Rank path and protein path.")
                st.stop()

            with st.spinner("Running P2Rank..."):

                pockets = get_pockets_from_local_protein(
                    protein_path,
                    p2rank_home=p2rank_home
                )

                st.session_state.pockets = pockets
                st.session_state.protein_path = protein_path


    # -------- UPLOAD MODE --------

    elif pocket_mode == "Upload Protein":

        uploaded_protein = st.file_uploader(
            "Upload Protein PDB",
            type=["pdb"],
            key="pocket_upload"
        )

        if st.button("Run Pocket Detection"):

            if not p2rank_home or uploaded_protein is None:
                st.warning("Provide P2Rank path and upload protein.")
                st.stop()

            with st.spinner("Running P2Rank..."):

                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdb") as tmp:
                    tmp.write(uploaded_protein.getbuffer())
                    tmp_path = tmp.name

                pockets = get_pockets_from_local_protein(
                    tmp_path,
                    p2rank_home=p2rank_home
                )

                st.session_state.pockets = pockets
                st.session_state.protein_path = tmp_path


    # -------- DISPLAY RESULTS --------

    if st.session_state.pockets:

        st.subheader("Top 3 Detected Pockets")

        pockets_dict = st.session_state.pockets
        pocket_list = list(pockets_dict.values())
        top_pockets = pocket_list[:3]

        for i, pocket in enumerate(top_pockets, start=1):
            st.write(f"### Pocket {i}")
            st.write(pocket)

        if st.session_state.protein_path:
            st.subheader("Protein Visualization")
            st_molstar(
                st.session_state.protein_path,
                key="persistent_pocket_viewer"
            )

# -------------------------------------------------
# DOCKING VIEWER
# -------------------------------------------------

elif page == "Docking Viewer":

    st.header("🔬 Docking Visualization")

    protein_upload = st.file_uploader(
        "Upload Protein (PDB)",
        type=["pdb"],
        key="dock_protein"
    )

    docking_upload = st.file_uploader(
        "Upload Docked Ligand (SDF)",
        type=["sdf"],
        key="dock_ligand"
    )

    gt_upload = st.file_uploader(
        "Upload Ground Truth Ligand (SDF)",
        type=["sdf"],
        key="dock_gt"
    )

    height = st.slider("Viewer Height", 200, 800, 400)

    submit_docking = st.button("Run Docking Visualization")

    if submit_docking:

        if protein_upload is None or docking_upload is None or gt_upload is None:
            st.warning("Please upload Protein, Docked Ligand, and Ground Truth files.")
            st.stop()

        with st.spinner("Preparing Docking Visualization..."):

            # Save protein temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdb") as tmp_prot:
                tmp_prot.write(protein_upload.getbuffer())
                protein_path = tmp_prot.name

            # Save docking temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".sdf") as tmp_dock:
                tmp_dock.write(docking_upload.getbuffer())
                docking_path = tmp_dock.name

            # Save ground truth temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".sdf") as tmp_gt:
                tmp_gt.write(gt_upload.getbuffer())
                gt_path = tmp_gt.name

            st_molstar_docking(
                protein_path,
                docking_path,
                gt_ligand_file_path=gt_path,
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
            "Enter URLs (one per line)"
        )

        files = [u.strip() for u in urls.split("\n") if u.strip()]

        if len(files) > 0:
            st_molstar_auto(files, key="auto_remote", height=f"{height}px")

    elif auto_mode == "Local Files":

        uploaded_files = st.file_uploader(
            "Upload Multiple Files",
            accept_multiple_files=True,
            key="auto_local"
        )

        if uploaded_files:
            st_molstar_auto(uploaded_files, key="auto_local_view", height=f"{height}px")

