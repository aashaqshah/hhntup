#!/bin/bash

# 2011
#grid-batch --dataset Ztautau_hadhad --metadata datasets.cfg --anti-match "*TPileupReweighting.prw.root*" --student HHSkim2 /global/endw/mc11_7TeV/higgs_tautau_hh_reskim_p851/user.NoelDawe.HHSkim.mc11_7TeV.125205.PowHegPythia_VBFH125_tautauhh.merge.NTUP_TAUMEDIUM.e893_s1310_s1300_r3043_r2993_p851.v7.120501172935
#grid-batch --dataset data11_hadhad --metadata datasets.cfg --student HHSkim2 /global/endw/data11_7TeV/higgs_tautau_hh_skim_p851/user.NoelDawe.HTauSkim.data11_7TeV.00191933.physics_JetTauEtmiss.merge.NTUP_TAUMEDIUM.f415_m1025_p851.v4.120204172411
#grid-batch --dataset embedding11_ztautau_p851_v1_skim --metadata datasets.cfg --student HHSkim2 /global/endw/embedding11_7TeV/test

# 2012
#grid-batch --dataset data12_p1011_hadhad_v1_skim --metadata datasets.cfg --student HHSkim2 /global/endw/data12_8TeV/skimtest
grid-batch --dataset data12_p1130_hadhad_v2_skim --metadata datasets.cfg --student HHSkim2 /global/oneil/hadhad/test/group.phys-higgs.HHSkim.data12_8TeV.00203680.physics_JetTauEtmiss.merge.NTUP_TAU.f446_m1148_p1130.v2.120720151724

#grid-batch --dataset mc12_p1011_hadhad_v1_skim --metadata datasets.cfg --student HHSkim2 /global/endw/mc12_8TeV/skimtest