# =================================================
# IMPORTS (ALL AT TOP)
# =================================================

import streamlit as st
import streamlit.components.v1 as components
import tempfile
import os

# Mol* components
from streamlit_molstar import (
    st_molstar,
    st_molstar_rcsb,
    st_molstar_remote
)
from streamlit_molstar.auto import st_molstar_auto
from streamlit_molstar.pocket import get_pockets_from_local_protein
from streamlit_molstar.docking import st_molstar_docking

# MDAnalysis
import MDAnalysis as mda
from MDAnalysis.analysis import rms
from MDAnalysis.analysis.rms import RMSF
import matplotlib.pyplot as plt

# RDKit
from rdkit import Chem, RDConfig
from rdkit.Chem import AllChem, ChemicalFeatures, Draw


# =================================================
# PAGE CONFIG
# =================================================

st.set_page_config(layout="wide", page_title="Mol* Molecular Suite")
st.title("🧬 Mol* Molecular Visualization Suite")


# =================================================
# SIDEBAR NAVIGATION
# =================================================

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
# 1️⃣ STRUCTURE VIEWER
# =================================================

if page == "Structure Viewer":

    st.header("🔎 Structure Viewer")

    mode = st.radio("Select Input Type", ["RCSB ID", "Remote URL"])

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
# 2️⃣ TRAJECTORY VIEWER
# =================================================

elif page == "Trajectory Viewer":

    st.header("🎞️ Trajectory Viewer (PDB + XTC)")

    topology_file = st.file_uploader("Upload Topology (PDB)", type=["pdb"])
    xtc_file = st.file_uploader("Upload Trajectory (XTC)", type=["xtc"])

    if st.button("Load Trajectory"):

        if topology_file is None or xtc_file is None:
            st.warning("Please upload both PDB and XTC files.")
            st.stop()

        # Save files
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdb") as tmp_pdb:
            tmp_pdb.write(topology_file.getbuffer())
            pdb_path = tmp_pdb.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=".xtc") as tmp_xtc:
            tmp_xtc.write(xtc_file.getbuffer())
            xtc_path = tmp_xtc.name

        # Mol* trajectory
        st.subheader("Molecular Trajectory")
        st_molstar(pdb_path, xtc_path, key="trajectory_view")

        # ---------------- MDAnalysis ----------------
        st.subheader("MD Analysis (Cα RMSD & RMSF)")

        with st.spinner("Computing RMSD and RMSF..."):

            u = mda.Universe(pdb_path, xtc_path)
            ca_atoms = u.select_atoms("name CA")

            # RMSD
            rmsd_analysis = rms.RMSD(
                u,
                u,
                select="name CA",
                ref_frame=0
            ).run()

            rmsd_values = rmsd_analysis.results.rmsd[:, 2]
            frames = rmsd_analysis.results.rmsd[:, 0]

            fig_rmsd = plt.figure()
            plt.plot(frames, rmsd_values)
            plt.xlabel("Frame")
            plt.ylabel("RMSD (Å)")
            plt.title("Cα RMSD vs Frame")
            st.pyplot(fig_rmsd)

            # RMSF
            rmsf_analysis = RMSF(ca_atoms).run()
            rmsf_values = rmsf_analysis.results.rmsf
            residue_ids = ca_atoms.resids

            fig_rmsf = plt.figure()
            plt.plot(residue_ids, rmsf_values)
            plt.xlabel("Residue ID")
            plt.ylabel("RMSF (Å)")
            plt.title("Cα RMSF")
            st.pyplot(fig_rmsf)


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

    st.header("🔬 Docking Viewer + Pharmacophore")

    protein_upload = st.file_uploader("Upload Protein (PDB)", type=["pdb"])
    docking_upload = st.file_uploader("Upload Docked Ligand (SDF)", type=["sdf"])
    gt_upload = st.file_uploader("Upload Ground Truth Ligand (SDF)", type=["sdf"])

    if st.button("Run Docking Visualization"):

        if protein_upload is None or docking_upload is None or gt_upload is None:
            st.warning("Upload protein, docked ligand, and ground truth ligand.")
            st.stop()

        # Save files
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdb") as tmp_prot:
            tmp_prot.write(protein_upload.getbuffer())
            protein_path = tmp_prot.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=".sdf") as tmp_dock:
            tmp_dock.write(docking_upload.getbuffer())
            docking_path = tmp_dock.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=".sdf") as tmp_gt:
            tmp_gt.write(gt_upload.getbuffer())
            gt_path = tmp_gt.name

        # Mol* docking view
        st.subheader("🧬 Protein–Ligand Docking (Mol*)")

        st_molstar_docking(
            protein_path,
            docking_path,
            gt_ligand_file_path=gt_path,
            key="docking_view"
        )

        # Pharmacophore
        st.subheader("🎯 Docked Ligand Pharmacophore")

        with st.spinner("Generating pharmacophore..."):

            fdefFile = os.path.join(RDConfig.RDDataDir, 'BaseFeatures.fdef')
            featFact = ChemicalFeatures.BuildFeatureFactory(fdefFile)

            mol = Chem.SDMolSupplier(docking_path)[0]

            if mol is None:
                st.error("Could not read docked ligand.")
                st.stop()

            AllChem.Compute2DCoords(mol)
            feats = featFact.GetFeaturesForMol(mol)

            def drawp4core(mol, feats):
                atoms_list = {}
                for feat in feats:
                    atoms_list[feat.GetType()] = feat.GetAtomIds()

                if not atoms_list:
                    return None

                return Draw.MolsToGridImage(
                    [mol] * len(atoms_list),
                    legends=list(atoms_list.keys()),
                    highlightAtomLists=list(atoms_list.values()),
                    molsPerRow=3,
                    subImgSize=(300, 300)
                )

            img = drawp4core(mol, feats)

            if img:
                st.image(img)
            else:
                st.warning("No pharmacophore features detected.")


# =================================================
# 5️⃣ AUTO VIEWER
# =================================================

elif page == "Auto Viewer":

    st.header("⚡ Auto File Viewer")

    uploaded_files = st.file_uploader(
        "Upload Multiple Files",
        accept_multiple_files=True
    )

    if st.button("Load Files"):

        if not uploaded_files:
            st.warning("Upload at least one file.")
            st.stop()

        file_paths = []

        for file in uploaded_files:
            suffix = "." + file.name.split(".")[-1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(file.getbuffer())
                file_paths.append(tmp.name)

        st_molstar_auto(file_paths, key="auto_view")
