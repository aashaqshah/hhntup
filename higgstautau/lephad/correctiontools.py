from rootpy.tree.filtering import *
from itertools import ifilter
from atlastools import utils
from atlastools.units import GeV
from atlastools import datasets
from math import *
from external.Muons     import muonSmear, getMuonSF, muonTriggerSF
from external.Electrons import egammaER
from external.ggF       import getggFTool
from ROOT import *




#################################################
# Muon Pt Smearing
#################################################

muonSmear.UseScale(1)
muonSmear.UseImprovedCombine()
muonSmear.RestrictCurvatureCorrections(2.5)
muonSmear.FillScales("KC")

class MuonPtSmearing(EventFilter):
    """
    Smears the Muon Pt using the official ATLAS tool
    """

    def __init__(self, datatype, **kwargs):

        super(MuonPtSmearing, self).__init__(**kwargs)
        self.datatype = datatype

    def passes(self, event):

        if self.datatype != datasets.MC: return True

        for mu in event.muons:

            #Obtain parameters for correction
            charge = mu.charge
            eta    = mu.eta
            pt     = mu.pt
            pt_ms  = sin(mu.ms_theta)/abs(mu.ms_qoverp)
            pt_id  = sin(mu.id_theta)/abs(mu.id_qoverp)

            #Seed with event number, reproducible smear for different analyses
            muonSmear.SetSeed(event.EventNumber)

            #Pass parameters, get smeared Pt
            muonSmear.Event(pt_ms, pt_id, pt, eta, charge)
            pt_smear = -1

            if mu.isCombinedMuon:
                pt_smear = muonSmear.pTCB()
            else:
                pt_smear = muonSmear.pTID()

            #Adjust Pt in transient D3PD
            mu.pt = pt_smear

            #Adjust MET accordingly
            px = pt*cos(mu.phi)
            py = pt*sin(mu.phi)

            px_smear = pt_smear*cos(mu.phi)
            py_smear = pt_smear*sin(mu.phi)

            event.MET_RefFinal_BDTMedium_etx += (px-px_smear)*mu.MET_BDTMedium_wpx[0]
            event.MET_RefFinal_BDTMedium_ety += (py-py_smear)*mu.MET_BDTMedium_wpx[0]
            event.MET_RefFinal_BDTMedium_sumet -= (pt-pt_smear)*mu.MET_BDTMedium_wet[0]

        return True



#################################################
# Electron Energy Rescaling
#################################################

class EgammaERescaling(EventFilter):
    """
    Rescales the electron energy using the official ATLAS tool
    """

    def __init__(self, datatype, **kwargs):

        super(EgammaERescaling, self).__init__(**kwargs)
        self.datatype = datatype

    def passes(self, event):

        # Seed with event number, reproducible smear for different analyses
        egammaER.SetRandomSeed(event.EventNumber)

        for el in event.electrons:

            # Obtain egamma raw Et to be corrected
            raw_e    = el.cl_E
            trk_eta  = el.tracketa
            trk_phi  = el.trackphi
            raw_et   = raw_e/cosh(trk_eta)
            raw_eta  = el.cl_eta
            raw_phi  = el.cl_phi
            corrected_e = -1

            # Treat MC first
            if self.datatype == datasets.MC:
                #Scaling correction
                new_et = egammaER.applyMCCalibrationMeV(raw_eta, raw_et, 'ELECTRON')
                new_e  = new_et*cosh(trk_eta)

                #Smearing correction
                sys = 0 # 0: nominal, 1: -1sigma, 2: +1sigma
                smearFactor = egammaER.getSmearingCorrectionMeV(raw_eta, new_e, sys, False, '2011')

                corrected_e = new_e*smearFactor

            # Treat Data
            else:
                #Calibration correction in data
                sys = 0 # 0: nominal, 1: -1sigma, 2: +1sigma
                new_e  = egammaER.applyEnergyCorrectionMeV(raw_eta, raw_phi, raw_e, raw_et, sys, 'ELECTRON')
                new_et = new_e/cosh(trk_eta)

                #Scaling correction
                scaleFactor = egammaER.applyMCCalibrationMeV(new_e, new_et, 'ELECTRON')

                corrected_e = new_e*scaleFactor

            # Modify E in transient D3PD
            el.cl_E = corrected_e
            corrected_et = corrected_e*cosh(trk_eta)
            
            #Adjust MET accordingly
            px = raw_et*cos(trk_phi)
            py = raw_et*sin(trk_phi)

            corrected_px = corrected_et*cos(trk_phi)
            corrected_py = corrected_et*sin(trk_phi)

            event.MET_RefFinal_BDTMedium_etx += (px-corrected_px)*el.MET_BDTMedium_wpx[0]
            event.MET_RefFinal_BDTMedium_ety += (py-corrected_py)*el.MET_BDTMedium_wpx[0]
            event.MET_RefFinal_BDTMedium_sumet -= (raw_et-corrected_et)*el.MET_BDTMedium_wet[0]
            
        return True



#################################################
# Tau/Electron Misidentification correction
#################################################
def TauEfficiencySF(event, datatype):
    """
    Apply Tau Efficiency Scale Factor correction
    """

    # Apply only on MC
    if datatype != datasets.MC: return 1.0

    for tau in event.taus:
        #Correct 1p taus/ electron fake rate
        #https://twiki.cern.ch/twiki/bin/viewauth/AtlasProtected/TauSystematicsWinterConf2012#Systematics_for_Electron_Misiden
        if tau.numTrack == 1 and tau.fourvect.Pt() > 20*GeV:
            nMC = event.mc_n
            for i in range(0, nMC):
                if abs(event.mc_pdgId[i]) == 11 and event.mc_pt[i] > 8*GeV:
                    if utils.dR(event.mc_eta[i], event.mc_phi[i], tau.eta, tau.phi) > 0.2: continue
                    if tau.eta < 1.37:
                        return 1.64
                    elif tau.eta < 1.52:
                        return 1.0
                    elif tau.eta < 2.0:
                        return 0.71
                    else:
                        return 2.9

    return 1.0



#################################################
# Muon Efficiency corrections
#################################################

def MuonSF(event, datatype, pileup_tool):
    """
    Apply Muon Efficiency correction for trigger and others
    """

    #Weight
    w = 1.0

    #Load muonSF tool
    muonSF = getMuonSF(pileup_tool)

    # Apply only on MC
    if datatype != datasets.MC: return 1.0

    #Store electrons and muons for the trigger efficiency tool
    std_muons     = std.vector(TLorentzVector)()
    std_electrons = std.vector(TLorentzVector)()

    for mu in event.muons:
        muon = TLorentzVector()
        muon.SetPtEtaPhiM(mu.pt, mu.eta, mu.phi, mu.m)
        std_muons.push_back(muon)
        w *= muonSF.scaleFactor(muon)

    for e in event.electrons:
        electron = TLorentzVector()
        cl_eta = e.cl_eta
        trk_eta = e.tracketa
        cl_Et = e.cl_E/cosh(trk_eta)
        electron.SetPtEtaPhiM(cl_Et, cl_eta, e.cl_phi, e.m)
        std_electrons.push_back(electron)

    trigSF = muonTriggerSF.GetTriggerSF(event.RunNumber, false, std_muons, 1, std_electrons, 2)
    w *= trigSF.first

    return w
    

#################################################
#ggF reweighting
#################################################

def ggFreweighting(event, dataname):
    """
    Reweight the ggF samples
    """

    if dataname.find('PowHegPythia_ggH') == -1: return 1.0

    #Extract mass value
    mass = int(dataname.lstrip('PowHegPythia_ggH').rstrip('_tautaulh.mc11c'))

    #Get corresponding ggF tool setting
    ggFTool = getggFTool(mass)

    #Find the Higgs particle in mc
    nMC = event.mc_n
    pt = 0
    for i in range(0, nMC):
        if event.mc_pdgId[i] == 25 and event.mc_status[i] != 3:
            pt = event.mc_pt[i]/1000

    if pt > 0:
        return ggFTool.getWeight(pt)
    else:
        return 1.0