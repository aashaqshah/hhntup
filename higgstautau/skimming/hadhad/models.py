import ROOT
from rootpy.tree import TreeModel
from rootpy.types import *


class SkimExtraModel(TreeModel):

    number_of_good_vertices = IntCol()


class SkimExtraTauPtModel(TreeModel):

    tau_pt = FloatCol()


class TriggerEmulation(TreeModel):

    EF_tau29_medium1_tau20_medium1_EMULATED = BoolCol()
    EF_tau29T_medium1_tau20T_medium1_EMULATED = BoolCol()
    tau_trigger_match_index = ROOT.vector('int')
    tau_trigger_match_thresh = ROOT.vector('int')


class TriggerMatching(TreeModel):

    tau_trigger_match_index = ROOT.vector('int')
    tau_trigger_match_thresh = ROOT.vector('int')


class Skim2Variables(TreeModel):

    tau_selected = ROOT.vector('bool')
    pileup_weight = FloatCol(default=1.)
