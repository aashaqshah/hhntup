REMOVE = [
    "cl_*",
    "ph_*",

    # these large mc branches are useless since
    # they contain barcodes and not indices
    # use mc_parent_index and mc_child_index
    "mc_children",
    "mc_parents",

    #"jet_AntiKt4TopoEM_*", <== jet cleaning recommendation is with TopoEM jets
    #"jet_AntiKt4LCTopo_*",  <== need these for MET systematics
    "jet_AntiKt6*",
    #"jet_flavor_*",  <== need these for systematics...
    "jet_*Assoc*",

    "tau_otherTrk_*",
    "tau_cell_*",
    "tau_cluster_*",

    "EF_2e*",
    "EF_2mu*",
    "EF_2j*",
    "EF_xe*",
    "EF_xs*",
    "EF_e*",
    "EF_mu*",
    "EF_MU*",
    "EF_g*",
    "EF_j*",
    "EF_g*",
    "L1_*",
    "L2_*",

    "muonTruth*",
    "jet_antikt4truth_*",
    "collcand_*",

    "el_*",
    "mu_*",
    "MET_*Reg*",

    "trk_*err*",
    "trk_*cov*",
]

# override globs above
KEEP = [
    "el_n",
    "el_cl_E",
    "el_tracketa",
    "el_trackphi",
    "el_author",
    "el_charge",
    "el_loosePP",
    "el_mediumPP",
    "el_tightPP",
    "el_OQ",
    # required for electron ID recalc
    "el_cl_eta",
    "el_cl_phi",
    "el_m",
    "el_deltaeta1",
    "el_deltaphi2",
    "el_Emax2",
    "el_emaxs1",
    "el_etas2",
    "el_Ethad",
    "el_Ethad1",
    "el_expectHitInBLayer",
    "el_f1",
    "el_f3",
    "el_isEM",
    "el_nBLayerOutliers",
    "el_nBLHits",
    "el_nPixelOutliers",
    "el_nPixHits",
    "el_nSCTOutliers",
    "el_nSiHits",
    "el_nTRTHits",
    "el_nTRTOutliers",
    "el_reta",
    "el_trackd0_physics",
    "el_trackqoverp",
    "el_TRTHighTOutliersRatio",
    "el_weta2",
    "el_wstot",

    "mu_staco_n",
    "mu_staco_E",
    "mu_staco_pt",
    "mu_staco_eta",
    "mu_staco_phi",
    "mu_staco_loose",
    "mu_staco_medium",
    "mu_staco_tight",
    "mu_staco_isSegmentTaggedMuon",
    "mu_staco_expectBLayerHit",
    "mu_staco_nBLHits",
    "mu_staco_nPixHits",
    "mu_staco_nPixelDeadSensors",
    "mu_staco_nSCTHits",
    "mu_staco_nSCTDeadSensors",
    "mu_staco_nPixHoles",
    "mu_staco_nSCTHoles",
    "mu_staco_nTRTHits",
    "mu_staco_nTRTOutliers",
]
