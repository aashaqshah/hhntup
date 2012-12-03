

HHSTUDENT ?= HHProcessor
HHNTUP ?= ntuples/hadhad/HHProcessor

default: clean

hh-ntup-clean:
	rm -f $(HHNTUP)/$(HHSTUDENT).root
	rm -f $(HHNTUP)/$(HHSTUDENT).h5

hh-ntup-merge: hh-ntup-clean
	./ntup-merge -s $(HHSTUDENT) $(HHNTUP)
	(cd $(HHNTUP) && root2hdf5 $(HHSTUDENT).root)

clean:
	rm -f *.pyc
	rm -f cutflow.p
	rm -f student*.root
	rm -f student*.profile
	rm -f TPileupReweighting.prw.root
	rm -f nohup.out
	rm -f supervisor*.log
	rm -f grid-setup.sh
	rm -f *.dot
