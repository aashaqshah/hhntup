"""
==================
Skimming procedure
==================

A) For DATA skimming:

1) Trigger

    The lowest un-prescaled trigger can be found in
    https://twiki.cern.ch/twiki/bin/viewauth/Atlas/LowestUnprescaled

    - Period A-I  :  tau29_medium1_tau20_medium1 || tau100_medium || xe60_noMu
    - Period J    :  tau29_medium1_tau20_medium1 || tau100_medium || xe60_tight_noMu
    - Period K    : tau29_medium1_tau20_medium1 || tau125_medium1 || xe60_tight_noMu
    - Period L-M  : tau29T_medium1_tau20T_medium1 || tau125_medium1 || xe60_verytight_noMu


2) Two LOOSE tau

    - tau_author!=2 && tau_pT > 18 GeV && tau_numTrack > 0
    - tau_JetBDTLoose==1 || tau_tauLlhLoose==1

    * Note pT>18GeV cut was chosen to be able to fluctuate the TES.

    With these two selection (1 & 2), we expect factor 50 reduction which
    results in ~400-500 GB disk space at 5 fb-1.


B) For MC skimming:

1) Trigger : OR of above.

==========
Histograms
==========

Some information has to be kept as "histogram" during the skimming.

Just after "Trigger" requirement, the histograms should be made according
to each trigger decision.  (three histograms for each variable)

 * number of events with GRL (to check consistency of LumiCalc)
 * mu-distribution
 * # of vertex
 * # of LOOSE tau (pt>18GeV, LLH||BDT-loose)
 * # of EF tau trigger object  (no matching is necessary)
 * tau pT spectrum
 * EF tau pT spectrum  (no matching is necessary)
 * MET
 * anything else???
"""


import ROOT
from atlastools import utils
from atlastools.units import *
from rootpy.tree.filtering import EventFilter, EventFilterList
from atlastools.batch import ATLASStudent
from rootpy.tree import Tree, TreeBuffer, TreeChain
from mixins import TauFourMomentum


ROOT.gErrorIgnoreLevel = ROOT.kFatal


class TriggerOR(EventFilter):

    def passes(self, event):
        """
        This method is generated dynamically based on which triggers
        are available in this given set of input files.
        This differs period to period.
        """
        return True
        

class TwoGoodLooseTaus(EventFilter):

    def passes(self, event):

        event.taus.select(lambda tau: tau.author != 2 and tau.numTrack > 0 and
                                      tau.pt > 18*GeV and (tau.tauLlhLoose == 1 or tau.JetBDTSigLoose == 1))
        return len(event.taus) > 1


triggers = [
    'EF_tau29T_medium1_tau20T_medium',
    'EF_tau125_medium1',
    'EF_xe60_verytight_noMu',
    'EF_tau29_medium1_tau20_medium1',
    'EF_e20_medium',
    'EF_e60_loose',
    'EF_xe60_noMu'
    ]


class HTauSkim(ATLASStudent):

    def work(self):
        
        # initialize the TreeChain of all input files (each containing one tree named self.fileset.treename)
        intree = TreeChain(self.fileset.treename,
                          files=self.fileset.files,
                          events=self.events)
        
        existing_triggers = ['event.%s' % trigger for trigger in triggers if (trigger in intree)]
        
        print "ORing these triggers:" 
        for trigger in existing_triggers:
            print "\t%s" % trigger
        
        if existing_triggers:
            or_cond = ' or '.join(existing_triggers)
            exec 'def or_passed(self, event): return %s' % or_cond
            TriggerOR.passes = or_passed

        self.output.cd()
        outtree = Tree(name=self.fileset.treename)
        outtree.set_buffer(intree.buffer, create_branches=True, visible=False)
        
        # set the event filters
        # passthrough for MC for trigger acceptance studies
        self.event_filters = EventFilterList([
            TriggerOR(),
            TwoGoodLooseTaus()
        ])
        intree.filters += self.event_filters

        # define tree collections
        intree.define_collection(name="taus", prefix="tau_", size="tau_n", mix=TauFourMomentum)

        # entering the main event loop...
        for event in intree:
            
            outtree.Fill()

        outtree.FlushBaskets()
        outtree.Write()
