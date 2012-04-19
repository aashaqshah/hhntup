"""
==================
Skimming procedure
==================

For DATA skimming:
------------------

    1) Triggers

        if 177986 <= event.RunNumber <= 187815: # Periods B-K
            return event.EF_tau29_medium1_tau20_medium1
        elif 188902 <= event.RunNumber <= 191933: # Periods L-M
            return event.EF_tau29T_medium1_tau20T_medium1

        See Triggers in filters.py

    2) Two LOOSE taus

        - tau_author!=2 && tau_pT > 18 GeV && tau_numTrack > 0
        - tau_JetBDTLoose==1 || tau_tauLlhLoose==1

        * Note pT>18GeV cut was chosen to be able to fluctuate the TES.

        With these two selection (1 & 2), we expect factor 50 reduction which
        results in ~400-500 GB disk space at 5 fb-1.


For MC skimming:
----------------

    1) Triggers: same as above.


======================
Extra Trees/Histograms
======================

Some information has to be kept during the skimming.

Just after the "Trigger" requirement, the histograms/trees should be made according
to each trigger decision.  (three histograms for each variable below)

 * number of events within GRL (to check consistency of LumiCalc)
 * mu-distribution
 * # of vertices
 * # of LOOSE taus (pt>18GeV, LLH loose || BDT loose)
 * # of EF tau trigger object  (no matching is necessary)
 * tau pT spectrum
 * EF tau pT spectrum  (no matching is necessary)
 * MET
 * anything else???


=================
Trigger Emulation
=================

Emulation is performed using the CoEPPTrigTool package

177531 - 178264 use the values in TrigTauHypo-00-02-35  (A-C)

179710 - 180776 use the values in TrigTauHypo-00-02-42  (D-E)

182013 - 191933 use the values in TrigTauHypo-00-03-02  (F-M)


==============
Branch removal
==============

See branches_remove and branches_keep below
"""

import ROOT
import math

from atlastools import utils
from atlastools import datasets
from atlastools.units import GeV
from atlastools.batch import ATLASStudent

from rootpy.tree.filtering import EventFilter, EventFilterList
from rootpy.tree import Tree, TreeChain, TreeModel
from rootpy.types import *
from rootpy.io import open as ropen
from rootpy.plotting import Hist

from higgstautau.mixins import TauFourMomentum
from higgstautau.hadhad.filters import Triggers
import goodruns

from externaltools import CoEPPTrigTool, PileupReweighting
from ROOT import Root
from ROOT import CoEPP


PileupReweighting = Root.TPileupReweighting

ROOT.gErrorIgnoreLevel = ROOT.kFatal

branches_remove = [
    "cl_*",
    "ph_*",

    "jet_AntiKt4TopoEM_*",
    "jet_AntiKt4LCTopo_*",
    "jet_AntiKt6*",
    "jet_flavor_*",
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
]

# override globs above
branches_keep = [
    "el_cl_E",
    "el_tracketa",
    "el_trackphi",
    "el_author",
    "el_charge",
    "el_loosePP",
    "el_mediumPP",
    "el_tightPP",
    "el_OQ",

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


class SkimExtraModel(TreeModel):

    number_of_good_vertices = IntCol()
    number_of_good_taus = IntCol()


class SkimExtraTauPtModel(TreeModel):

    tau_pt = FloatCol()


class HHSkim(ATLASStudent):

    def work(self):

        # merge TrigConfTrees
        metadirname = '%sMeta' % self.metadata.treename
        trigconfchain = ROOT.TChain('%s/TrigConfTree' % metadirname)
        map(trigconfchain.Add, self.files)
        metadir = self.output.mkdir(metadirname)
        metadir.cd()
        trigconfchain.Merge(self.output, -1, 'fast keep')
        self.output.cd()

        if self.metadata.datatype == datasets.DATA:
            # merge GRL XML strings
            grls = []
            merged_grl = goodruns.GRL()
            for fname in self.files:
                merged_grl |= goodruns.GRL('%s:/Lumi/%s' % (fname, self.metadata.treename))
            lumi_dir = self.output.mkdir('Lumi')
            lumi_dir.cd()
            xml_string= ROOT.TObjString(merged_grl.str())
            xml_string.Write(self.metadata.treename)
            self.output.cd()

        onfilechange = []

        if self.metadata.datatype == datasets.MC:
            # initialize the pileup reweighting tool
            pileup_tool = PileupReweighting()
            pileup_tool.UsePeriodConfig("MC11b")
            pileup_tool.Initialize()

            # initialize the trigger emulation tool
            trigger_tool_wrapper = CoEPP.OfficialWrapper()
            trigger_tool = CoEPP.TriggerTool()
            trigger_tool.setWrapper(trigger_tool_wrapper)
            trigger_config = CoEPPTrigTool.get_resource('tute05_config.xml')
            trigger_tool.setXMLFile(trigger_config)
            trigger_tool.initializeFromXML()
            trigger = trigger_tool.getTriggerChecked("EF_tau29_medium1_tau20_medium1_Hypo_00_03_02")
            trigger.switchOn()

            def update_trigger_trees(student, trigger_tool_wrapper, name, file, tree):

                trigger_tool_wrapper.loadMainTree(tree)
                trigger_tool_wrapper.loadMetaTree(file.Get('%s/TrigConfTree' % name))

            onfilechange.append((update_trigger_trees, (self, trigger_tool_wrapper,)))

        # initialize the TreeChain of all input files
        intree = TreeChain(self.metadata.treename,
                           files=self.files,
                           events=self.events,
                           onfilechange=onfilechange)

        outtree = Tree(name=self.metadata.treename,
                       file=self.output,
                       model=SkimExtraModel)

        removed_branches = intree.glob(branches_remove, prune=branches_keep)

        outtree.set_buffer(intree.buffer,
                           ignore_variables=removed_branches,
                           create_branches=True,
                           visible=False)

        if self.metadata.datatype == datasets.DATA:
            # outtree_extra holds info for events not included in the skim
            outtree_extra = Tree(name=self.metadata.treename + '_failed_skim_after_trigger',
                                 file=self.output,
                                 model=SkimExtraModel + SkimExtraTauPtModel)

            extra_variables = [
                'trig_EF_tau_pt',
                'actualIntPerXing',
                'averageIntPerXing',
                'MET_RefFinal_BDTMedium_phi',
                'MET_RefFinal_BDTMedium_et'
                'MET_RefFinal_BDTMedium_sumet',
                'EventNumber',
                'RunNumber',
                'lbn'
            ] + Triggers.triggers

            outtree_extra.set_buffer(intree.buffer, variables=extra_variables, create_branches=True, visible=False)

        # set the event filters
        trigger_filter = Triggers()

        # define tau collection
        intree.define_collection(name='taus', prefix='tau_', size='tau_n', mix=TauFourMomentum)
        intree.define_collection(name='vertices', prefix='vxp_', size='vxp_n')

        nevents = 0
        nevents_mc_weight = 0
        # entering the main event loop...
        for event in intree:

            nevents += 1

            if self.metadata.datatype == datasets.MC:
                nevents_mc_weight += event.mc_event_weight
                pileup_tool.Fill(event.RunNumber, event.mc_channel_number,
                                 event.mc_event_weight, event.averageIntPerXing);

                trigger_tool_wrapper.setEventNumber(event._entry.value)
                trigger_tool.executeTriggers()

            if (self.metadata.datatype == datasets.MC and trigger_tool.passed()) or trigger_filter(event):
                event.vertices.select(lambda vxp: (vxp.type == 1 and vxp.nTracks >= 4) or (vxp.type == 3 and vxp.nTracks >= 2))
                number_of_good_vertices = len(event.vertices)
                event.taus.select(lambda tau: tau.author != 2 and tau.numTrack > 0 and
                                              tau.pt > 18*GeV and
                                              (tau.tauLlhLoose == 1 or tau.JetBDTSigLoose == 1))
                number_of_good_taus = len(event.taus)
                if (number_of_good_taus > 1 and self.metadata.datatype == datasets.DATA) or \
                    self.metadata.datatype == datasets.MC:
                    outtree.number_of_good_vertices = number_of_good_vertices
                    outtree.number_of_good_taus = number_of_good_taus
                    outtree.Fill()
                else:
                    outtree_extra.number_of_good_vertices = number_of_good_vertices
                    outtree_extra.number_of_good_taus = number_of_good_taus
                    if event.taus:
                        # There can be at most one good tau if this event failed the skim
                        outtree_extra.tau_pt = event.taus[0].pt
                    else:
                        outtree_extra.tau_pt = -1111.
                    outtree_extra.Fill()

        self.output.cd()

        if self.metadata.datatype == datasets.MC:
            # store the original weighted number of events
            cutflow = Hist(2, 0, 2, name='cutflow', type='D')
            cutflow[1] = nevents_mc_weight
        else:
            cutflow = Hist(1, 0, 1, name='cutflow', type='D')
        # store the original number of events
        cutflow[0] = nevents
        cutflow.Write()

        # flush any baskets remaining in memory to disk
        outtree.FlushBaskets()
        outtree.Write()
        if self.metadata.datatype == datasets.DATA:
            outtree_extra.FlushBaskets()
            outtree_extra.Write()

        if self.metadata.datatype == datasets.MC:
            # write the pileup reweighting file
            pileup_tool.WriteToFile()

            # finalize the trigger_tool
            trigger_tool.finalize()
            trigger_tool.summary()
