"""
This module defines the output branches in the final ntuple
as TreeModels.
"""

from rootpy.tree import TreeModel, FloatCol, IntCol, DoubleCol, BoolCol
from rootpy import stl
from rootpy.vector import (
    LorentzRotation, LorentzVector, Vector3, Vector2)
from rootpy import log
ignore_warning = log['/ROOT.TVector3.PseudoRapidity'].ignore(
    '.*transvers momentum.*')

from ..utils import et2pt
from .. import datasets
from .. import utils
from .. import eventshapes
from ..models import MatchedObject

import math
import ROOT
from ROOT import TLorentzVector


class FourMomentum(TreeModel):
    pt = FloatCol()
    p = FloatCol()
    et = FloatCol()
    e = FloatCol()
    eta = FloatCol(default=-1111)
    phi = FloatCol(default=-1111)
    m = FloatCol()

    @classmethod
    def set(cls, this, other):
        if isinstance(other, TLorentzVector):
            vect = other
        else:
            vect = other.fourvect
        this.pt = vect.Pt()
        this.p = vect.P()
        this.et = vect.Et()
        this.e = vect.E()
        this.m = vect.M()
        with ignore_warning:
            this.phi = vect.Phi()
            this.eta = vect.Eta()


class TrueTau(TreeModel):
    nProng = IntCol(default=-1111)
    nPi0 = IntCol(default=-1111)
    charge = IntCol()


class MMCOutput(FourMomentum.prefix('resonance_')):
    mass = FloatCol()
    MET_et = FloatCol()
    MET_etx = FloatCol()
    MET_ety = FloatCol()
    MET_phi = FloatCol()


class MMCModel(MMCOutput.prefix('mmc0_'),
               MMCOutput.prefix('mmc1_'),
               MMCOutput.prefix('mmc2_')):
    pass


class MassModel(MMCModel):
    mass_collinear_tau1_tau2 = FloatCol()
    mass_vis_tau1_tau2 = FloatCol()
    mass_jet1_jet2 = FloatCol(default=-1E10)
    mass_tau1_tau2_jet1 = FloatCol(default=-1E10)
    #mass_vis_true_tau1_tau2 = FloatCol()
    #mass_true_quark1_quark2 = FloatCol()


class METModel(TreeModel):
    MET_et = FloatCol()
    MET_etx = FloatCol()
    MET_ety = FloatCol()
    MET_sumet = FloatCol()
    MET_phi = FloatCol()
    MET_sig = FloatCol()

    MET_et_original = FloatCol()
    MET_etx_original = FloatCol()
    MET_ety_original = FloatCol()
    MET_sumet_original = FloatCol()
    MET_phi_original = FloatCol()

    dPhi_tau1_MET = FloatCol()
    dPhi_tau2_MET = FloatCol()
    dPhi_min_tau_MET = FloatCol()
    MET_bisecting = BoolCol()

    MET_centrality = FloatCol(default=-1E10)
    MET_centrality_boosted = FloatCol(default=-1E10)


class EmbeddingModel(TreeModel):
    # embedding corrections
    embedding_reco_unfold = FloatCol(default=1.)
    embedding_trigger_weight = FloatCol(default=1.)
    embedding_dimuon_mass = FloatCol()
    embedding_isolation = IntCol()
    embedding_spin_weight = FloatCol(default=1.)


class RecoTau(FourMomentum):
    index = IntCol(default=-1)

    BDTJetScore = FloatCol()
    BDTEleScore = FloatCol()

    JetBDTSigLoose = BoolCol()
    JetBDTSigMedium = BoolCol()
    JetBDTSigTight = BoolCol()
    id = IntCol()

    nPi0 = IntCol()
    seedCalo_numTrack = IntCol()
    numTrack = IntCol()
    charge = IntCol()
    jvtxf = FloatCol()
    seedCalo_centFrac = FloatCol()

    BCHMedium = BoolCol()
    BCHTight = BoolCol()

    centrality = FloatCol(default=-1E10)
    centrality_boosted = FloatCol(default=-1E10)

    # efficiency scale factor if matches truth
    id_sf = FloatCol(default=1.)
    id_sf_high = FloatCol(default=1.)
    id_sf_low = FloatCol(default=1.)
    id_sf_stat_high = FloatCol(default=1.)
    id_sf_stat_low = FloatCol(default=1.)
    id_sf_sys_high = FloatCol(default=1.)
    id_sf_sys_low = FloatCol(default=1.)

    # trigger efficiency
    trigger_sf = FloatCol(default=1.)
    trigger_sf_high = FloatCol(default=1.)
    trigger_sf_low = FloatCol(default=1.)
    trigger_sf_mc_stat_high = FloatCol(default=1.)
    trigger_sf_mc_stat_low = FloatCol(default=1.)
    trigger_sf_data_stat_high = FloatCol(default=1.)
    trigger_sf_data_stat_low = FloatCol(default=1.)
    trigger_sf_stat_high = FloatCol(default=1.)
    trigger_sf_stat_low = FloatCol(default=1.)
    trigger_sf_sys_high = FloatCol(default=1.)
    trigger_sf_sys_low = FloatCol(default=1.)

    trigger_eff = FloatCol(default=1.)
    trigger_eff_high = FloatCol(default=1.)
    trigger_eff_low = FloatCol(default=1.)
    trigger_eff_stat_high = FloatCol(default=1.)
    trigger_eff_stat_low = FloatCol(default=1.)
    trigger_eff_sys_high = FloatCol(default=1.)
    trigger_eff_sys_low = FloatCol(default=1.)

    # fake rate scale factor for taus that do not match truth
    fakerate_sf = FloatCol(default=1.)
    fakerate_sf_high = FloatCol(default=1.)
    fakerate_sf_low = FloatCol(default=1.)

    # fake rate reco scale factor for taus that do not match truth
    fakerate_sf_reco = FloatCol(default=1.)
    fakerate_sf_reco_high = FloatCol(default=1.)
    fakerate_sf_reco_low = FloatCol(default=1.)

    #trigger_match_thresh = IntCol(default=0)

    # overlap checking
    min_dr_jet = FloatCol(default=9999)

    # track recounting
    numTrack_recounted = IntCol(default=-1)

    # vertex association
    vertex_prob = FloatCol()

    collinear_momentum_fraction = FloatCol()


class RecoJet(FourMomentum):
    index = IntCol(default=-1)
    jvtxf = FloatCol()
    BDTJetScore = FloatCol()
    BCHMedium = BoolCol()
    BCHTight = BoolCol()


class RecoTauBlock((RecoTau + MatchedObject).prefix('tau1_') +
                   (RecoTau + MatchedObject).prefix('tau2_')):

    #tau_trigger_match_error = BoolCol(default=False)

    # did both taus come from the same vertex?
    tau_same_vertex = BoolCol()

    theta_tau1_tau2 = FloatCol()
    cos_theta_tau1_tau2 = FloatCol()
    tau_pt_ratio = FloatCol()

    @classmethod
    def set(cls, event, tree, tau1, tau2, skim):
        tree.theta_tau1_tau2 = abs(tau1.fourvect.Angle(tau2.fourvect))
        tree.cos_theta_tau1_tau2 = math.cos(tree.theta_tau1_tau2)
        tree.dR_tau1_tau2 = tau1.fourvect.DeltaR(tau2.fourvect)
        tree.dEta_tau1_tau2 = abs(tau2.eta - tau1.eta)
        # leading pt over subleading pt
        tree.tau_pt_ratio = tau1.pt / tau2.pt

        for outtau, intau in [(tree.tau1, tau1), (tree.tau2, tau2)]:

            outtau.index = intau.index
            outtau.id = intau.id

            FourMomentum.set(outtau, intau)

            outtau.BDTJetScore = intau.BDTJetScore
            outtau.BDTEleScore = intau.BDTEleScore

            outtau.JetBDTSigLoose = intau.JetBDTSigLoose
            outtau.JetBDTSigMedium = intau.JetBDTSigMedium
            outtau.JetBDTSigTight = intau.JetBDTSigTight

            outtau.nPi0 = intau.nPi0
            outtau.seedCalo_numTrack = intau.seedCalo_numTrack
            outtau.numTrack = intau.numTrack
            outtau.charge = intau.charge
            outtau.jvtxf = intau.jet_jvtxf
            outtau.seedCalo_centFrac = intau.seedCalo_centFrac

            outtau.BCHMedium = intau.BCHMedium
            outtau.BCHTight = intau.BCHTight

            outtau.centrality = intau.centrality
            outtau.centrality_boosted = intau.centrality_boosted

            if intau.matched:
                outtau.id_sf = intau.id_sf
                outtau.id_sf_high = intau.id_sf_high
                outtau.id_sf_low = intau.id_sf_low
                outtau.id_sf_stat_high = intau.id_sf_stat_high
                outtau.id_sf_stat_low = intau.id_sf_stat_low
                outtau.id_sf_sys_high = intau.id_sf_sys_high
                outtau.id_sf_sys_low = intau.id_sf_sys_low

                outtau.trigger_sf = intau.trigger_sf
                outtau.trigger_sf_high = intau.trigger_sf_high
                outtau.trigger_sf_low = intau.trigger_sf_low
                outtau.trigger_sf_mc_stat_high = intau.trigger_sf_mc_stat_high
                outtau.trigger_sf_mc_stat_low = intau.trigger_sf_mc_stat_low
                outtau.trigger_sf_data_stat_high = intau.trigger_sf_data_stat_high
                outtau.trigger_sf_data_stat_low = intau.trigger_sf_data_stat_low
                outtau.trigger_sf_sys_high = intau.trigger_sf_sys_high
                outtau.trigger_sf_sys_low = intau.trigger_sf_sys_low

                outtau.trigger_eff = intau.trigger_eff
                outtau.trigger_eff_high = intau.trigger_eff_high
                outtau.trigger_eff_low = intau.trigger_eff_low
                outtau.trigger_eff_stat_high = intau.trigger_eff_stat_high
                outtau.trigger_eff_stat_low = intau.trigger_eff_stat_low
                outtau.trigger_eff_sys_high = intau.trigger_eff_sys_high
                outtau.trigger_eff_sys_low = intau.trigger_eff_sys_low

            else:
                outtau.fakerate_sf = intau.fakerate_sf
                outtau.fakerate_sf_high = intau.fakerate_sf_high
                outtau.fakerate_sf_low = intau.fakerate_sf_low

                outtau.fakerate_sf_reco = intau.fakerate_sf_reco
                outtau.fakerate_sf_reco_high = intau.fakerate_sf_reco_high
                outtau.fakerate_sf_reco_low = intau.fakerate_sf_reco_low

            #outtau.trigger_match_thresh = intau.trigger_match_thresh

            outtau.matched = intau.matched
            outtau.matched_dR = intau.matched_dR
            outtau.matched_collision = intau.matched_collision
            outtau.min_dr_jet = intau.min_dr_jet

            if skim:
                # track recounting
                # the track branches are removed by the skim, so this should
                # only be set in the skim and cannot be recomputed on the skim
                outtau.numTrack_recounted = intau.numTrack_recounted

            # tau vertex association
            outtau.vertex_prob = intau.vertex_prob

            outtau.collinear_momentum_fraction = intau.collinear_momentum_fraction


class RecoJetBlock(RecoJet.prefix('jet1_') +
                   RecoJet.prefix('jet2_') +
                   RecoJet.prefix('jet3_')):
    #jet_transformation = LorentzRotation
    jet_beta = Vector3
    #parton_beta = Vector3
    numJets = IntCol()
    nonisolatedjet = BoolCol()
    jet3_centrality = FloatCol(default=-1E10)
    jet3_centrality_boosted = FloatCol(default=-1E10)

    @classmethod
    def set(cls, tree, jet1, jet2=None, jet3=None):
        FourMomentum.set(tree.jet1, jet1)
        tree.jet1_jvtxf = jet1.jvtxf
        tree.jet1_index = jet1.index
        tree.jet1_BCHMedium = jet1.BCHMedium
        tree.jet1_BCHTight = jet1.BCHTight

        if jet2 is None:
            return

        FourMomentum.set(tree.jet2, jet2)
        tree.jet2_jvtxf = jet2.jvtxf
        tree.jet2_index = jet2.index
        tree.jet2_BCHMedium = jet2.BCHMedium
        tree.jet2_BCHTight = jet2.BCHTight

        tree.mass_jet1_jet2 = (jet1.fourvect + jet2.fourvect).M()

        tree.dEta_jets = abs(
            jet1.fourvect.Eta() - jet2.fourvect.Eta())
        tree.dEta_jets_boosted = abs(
            jet1.fourvect_boosted.Eta() - jet2.fourvect_boosted.Eta())

        tree.eta_product_jets = jet1.fourvect.Eta() * jet2.fourvect.Eta()
        tree.eta_product_jets_boosted = (
            jet1.fourvect_boosted.Eta() * jet2.fourvect_boosted.Eta())

        if jet3 is None:
            return

        FourMomentum.set(tree.jet3, jet3)
        tree.jet3_jvtxf = jet3.jvtxf
        tree.jet3_index = jet3.index
        tree.jet3_BCHMedium = jet3.BCHMedium
        tree.jet3_BCHTight = jet3.BCHTight

        # eta centrality of 3rd leading jet
        tree.jet3_centrality = eventshapes.eta_centrality(
            jet3.fourvect.Eta(),
            jet1.fourvect.Eta(),
            jet2.fourvect.Eta())
        tree.jet3_centrality_boosted = eventshapes.eta_centrality(
            jet3.fourvect_boosted.Eta(),
            jet1.fourvect_boosted.Eta(),
            jet2.fourvect_boosted.Eta())


class TrueTauBlock((TrueTau + MatchedObject).prefix('truetau1_') +
                   (TrueTau + MatchedObject).prefix('truetau2_')):

    @classmethod
    def set(cls, tree, index, tau):
        setattr(tree, 'truetau%i_nProng' % index, tau.nProng)
        setattr(tree, 'truetau%i_nPi0' % index, tau.nPi0)
        setattr(tree, 'truetau%i_charge' % index, tau.charge)

        fourvect = getattr(tree, 'truetau%i_fourvect' % index)
        fourvect.SetPtEtaPhiM(
            tau.pt,
            tau.eta,
            tau.phi,
            tau.m)

        fourvect_boosted = getattr(tree, 'truetau%i_fourvect_boosted' % index)
        fourvect_boosted.copy_from(fourvect)
        fourvect_boosted.Boost(tree.parton_beta * -1)

        fourvect_vis = getattr(tree, 'truetau%i_fourvect_vis' % index)
        try:
            fourvect_vis.SetPtEtaPhiM(
                et2pt(tau.vis_Et, tau.vis_eta, tau.vis_m),
                tau.vis_eta,
                tau.vis_phi,
                tau.vis_m)
        except ValueError:
            print "DOMAIN ERROR ON TRUTH 4VECT"
            print tau.vis_Et, tau.vis_eta, tau.vis_m
        else:
            fourvect_vis_boosted = getattr(tree, 'truetau%i_fourvect_vis_boosted' % index)
            fourvect_vis_boosted.copy_from(fourvect_vis)
            fourvect_vis_boosted.Boost(tree.parton_beta * -1)


class EventModel(TreeModel):
    trigger = BoolCol(default=True)

    RunNumber = IntCol()
    number_of_good_vertices = IntCol()
    averageIntPerXing = FloatCol()
    actualIntPerXing = FloatCol()

    nvtxsoftmet = IntCol()
    nvtxjets = IntCol()

    # event weight given by the PileupReweighting tool
    pileup_weight = FloatCol(default=1.)
    pileup_weight_high = FloatCol(default=1.)
    pileup_weight_low = FloatCol(default=1.)

    mc_weight = FloatCol(default=1.)

    #dR_quarks = FloatCol()
    #dR_truetaus = FloatCol()
    #dR_taus = FloatCol()
    #dR_jets = FloatCol()
    #dR_quark_tau = FloatCol()
    dR_tau1_tau2 = FloatCol()
    dEta_tau1_tau2 = FloatCol()
    dPhi_tau1_tau2 = FloatCol()

    #dEta_quarks = FloatCol(default=-1)
    dEta_jets = FloatCol(default=-1)
    dEta_jets_boosted = FloatCol()
    eta_product_jets = FloatCol(default=-1E10)
    eta_product_jets_boosted = FloatCol(default=-1E10)

    #sphericity = FloatCol(default=-1)
    #aplanarity = FloatCol(default=-1)

    #sphericity_boosted = FloatCol(default=-1)
    #aplanarity_boosted = FloatCol(default=-1)

    #sphericity_full = FloatCol(default=-1)
    #aplanarity_full = FloatCol(default=-1)

    sum_pt = FloatCol()
    sum_pt_full = FloatCol()
    vector_sum_pt = FloatCol()
    vector_sum_pt_full = FloatCol()
    resonance_pt = FloatCol()
    true_resonance_pt = FloatCol()
    num_true_jets_no_overlap = IntCol()

    ntrack_pv = IntCol()
    ntrack_nontau_pv = IntCol()

    jet_E_original = stl.vector('float')
    jet_m_original = stl.vector('float')
    jet_pt_original = stl.vector('float')
    jet_eta_original = stl.vector('float')
    jet_phi_original = stl.vector('float')

    error = BoolCol()


def get_model(datatype, name, prefix=None):
    model = EventModel + MassModel + METModel + RecoTauBlock + RecoJetBlock
    #if datatype != datasets.DATA:
    #    model += TrueTauBlock
    if datatype in (datasets.EMBED, datasets.MCEMBED):
        model += EmbeddingModel
    #if datatype == datasets.MC and 'VBF' in name:
    #    # add branches for VBF Higgs associated partons
    #    model += PartonBlock
    if prefix is not None:
        return model.prefix(prefix)
    return model
