# --
# February 16th, 2015: xAOD filter using AsgTool implemented
# --
from rootpy.tree.filtering import EventFilter
from rootpy import stl

import ROOT

from . import datasets
from . import log; log = log[__name__]
import os

# https://twiki.cern.ch/twiki/bin/viewauth/AtlasProtected/InDetTrackingPerformanceGuidelines
PU_RESCALE = {
    2011: (0.97, 0.01),
    2012: (1.09, 0.04),
}

PILEUP_TOOLS = []


def get_pileup_reweighting_tool(year, use_defaults=True, systematic=None):
    # https://twiki.cern.ch/twiki/bin/viewauth/AtlasProtected/ExtendedPileupReweighting
    # Initialize the pileup reweighting tool
    pileup_tool = Root.TPileupReweighting()
    if year == 2011:
        if use_defaults:
            pileup_tool.AddConfig(os.path.join(
                os.getenv('ROOTCOREDIR'),
                'data/PileupReweighting/mc11b_defaults.prw.root'))
        else:
            pileup_tool.AddConfigFile(
                'lumi/2011/'
                'TPileupReweighting.mc11.prw.root')
        lumicalc_file = 'lumi/2011/ilumicDDalc_histograms_None_178044-191933.root'
    elif year == 2012:
        if use_defaults:
            pileup_tool.AddConfig(os.path.join(
                os.getenv('ROOTCOREDIR'),
                'data/PileupReweighting/mc12ab_defaults.prw.root'))
        else:
            pileup_tool.AddConfigFile(
                'lumi/2012/'
                'TPileupReweighting.mc12.prw.root')
        lumicalc_file = 'lumi/2012/ilumicalc_histograms_None_200842-215643.root'
    else:
        raise ValueError(
            'No pileup reweighting defined for year %d' % year)
    rescale, rescale_error = PU_RESCALE[year]
    if systematic is None:
        pileup_tool.SetDataScaleFactors(1. / rescale)
    elif systematic == 'high':
        pileup_tool.SetDataScaleFactors(1. / (rescale + rescale_error))
    elif systematic == 'low':
        pileup_tool.SetDataScaleFactors(1. / (rescale - rescale_error))
    else:
        raise ValueError(
            "pileup systematic '{0}' not understood".format(systematic))
    pileup_tool.AddLumiCalcFile(lumicalc_file)
    # discard unrepresented data (with mu not simulated in MC)
    pileup_tool.SetUnrepresentedDataAction(2)
    pileup_tool.Initialize()
    # set the random seed used by the GetRandomRunNumber and
    # GetRandomPeriodNumber methods
    pileup_tool.SetRandomSeed(1777)
    # register
    PILEUP_TOOLS.append(pileup_tool)
    return pileup_tool


class PileupTemplates(EventFilter):

    def __init__(self, year, passthrough=False, **kwargs):
        if not passthrough:
            # initialize the pileup reweighting tool
            self.pileup_tool = Root.TPileupReweighting()
            if year == 2011:
                self.pileup_tool.UsePeriodConfig("MC11b")
            elif year == 2012:
                self.pileup_tool.UsePeriodConfig("MC12a")
            self.pileup_tool.Initialize()
        super(PileupTemplates, self).__init__(
            passthrough=passthrough,
            **kwargs)

    def passes(self, event):
        # XAOD MIGRATION: hard coding of the runnumber and channel for now
        self.pileup_tool.Fill(
            195847,
            161656,
            #     event.EventInfo.runNumber(),
            # event.EventInfo.mcChannelNumber(),
            event.EventInfo.mcEventWeight(),
            event.EventInfo.averageInteractionsPerCrossing())
        return True

    def finalize(self):
        if not self.passthrough:
            # write the pileup reweighting file
            self.pileup_tool.WriteToFile()


class PileupReweight(EventFilter):
    # XAOD MIGRATION: hard coding of the runnumber and channel for now
    """
    Currently only implements hadhad reweighting
    """
    def __init__(self, year, tool, tool_high, tool_low,
                 tree, passthrough=False, **kwargs):
        if not passthrough:
            self.tree = tree
            self.tool = tool
            self.tool_high = tool_high
            self.tool_low = tool_low
        super(PileupReweight, self).__init__(
            passthrough=passthrough,
            **kwargs)

    def passes(self, event):
        # set the pileup weights
        self.tree.pileup_weight = self.tool.GetCombinedWeight(
            195847,
            161656,
            # event.EventInfo.runNumber(),
            # event.EventInfo.mcChannelNumber(),
            event.EventInfo.averageInteractionsPerCrossing())
        self.tree.pileup_weight_high = self.tool_high.GetCombinedWeight(
            195847,
            161656,
            # event.EventInfo.runNumber(),
            # event.EventInfo.mcChannelNumber(),
            event.EventInfo.averageInteractionsPerCrossing())
        self.tree.pileup_weight_low = self.tool_low.GetCombinedWeight(
            195847,
            161656,
            # event.EventInfo.runNumber(),
            # event.EventInfo.mcChannelNumber(),
            event.EventInfo.averageInteractionsPerCrossing())
        return True


class PileupScale(EventFilter):

    def __init__(self, tree, year, datatype, **kwargs):
        self.tree = tree
        self.scale = PU_RESCALE[year][0]
        super(PileupScale, self).__init__(**kwargs)
        if datatype in (datasets.DATA, datasets.EMBED):
            self.passes = self.passes_data
        elif datatype in (datasets.MC, datasets.MCEMBED):
            self.passes = self.passes_mc
        else:
            raise ValueError("no pileup scale defined for datatype %d" %
                datatype)

    def passes_data(self, event):
        self.tree.averageIntPerXing = event.EventInfo.averageInteractionsPerCrossing()
        self.tree.actualIntPerXing = event.EventInfo.actualInteractionsPerCrossing()
        return True

    def passes_mc(self, event):
        self.tree.averageIntPerXing = event.EventInfo.averageInteractionsPerCrossing() * self.scale
        self.tree.actualIntPerXing = event.EventInfo.actualInteractionsPerCrossing() * self.scale
        return True


class PileupReweight(EventFilter):
    # XAOD MIGRATION: hard coding of the runnumber and channel for now
    # Will move to the XAOD tool once available in python
    """
    Currently only implements hadhad reweighting
    """
    def __init__(self, year, tool, tool_high, tool_low,
                 tree, passthrough=False, **kwargs):
        if not passthrough:
            self.tree = tree
            self.tool = tool
            self.tool_high = tool_high
            self.tool_low = tool_low
        super(PileupReweight, self).__init__(
            passthrough=passthrough,
            **kwargs)

    def passes(self, event):
        # set the pileup weights
        self.tree.pileup_weight = self.tool.GetCombinedWeight(
            195847,
            161656,
            # event.EventInfo.runNumber(),
            # event.EventInfo.mcChannelNumber(),
            event.EventInfo.averageInteractionsPerCrossing())
        self.tree.pileup_weight_high = self.tool_high.GetCombinedWeight(
            195847,
            161656,
            # event.EventInfo.runNumber(),
            # event.EventInfo.mcChannelNumber(),
            event.EventInfo.averageInteractionsPerCrossing())
        self.tree.pileup_weight_low = self.tool_low.GetCombinedWeight(
            195847,
            161656,
            # event.EventInfo.runNumber(),
            # event.EventInfo.mcChannelNumber(),
            event.EventInfo.averageInteractionsPerCrossing())
        return True


class PileupReweight_xAOD(EventFilter):

    def __init__(self, tree, **kwargs):
        super(PileupReweight_xAOD, self).__init__(**kwargs)

        self.tree = tree
        self.pileup_tool = ROOT.CP.PileupReweightingTool('pileup_tool')

        mc_vec = stl.vector('string')()
        data_vec = stl.vector('string')()
        mc_vec.push_back('PileupReweighting/mc14v1_defaults.prw.root')
        data_vec.push_back('lumi/2012/ilumicalc_histograms_None_200842-215643.root')

        self.pileup_tool.setProperty('ConfigFiles', mc_vec)
        self.pileup_tool.setProperty('LumiCalcFiles', data_vec)
        self.pileup_tool.setProperty('int')('DefaultChannel', 161656)
        self.pileup_tool.initialize()

    def passes(self, event):
        self.pileup_tool.apply(event.EventInfo)
        self.tree.pileup_weight = event.EventInfo.auxdataConst('double')( "PileupWeight" )
        return True

