#!/usr/bin/env python

from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('--student', default='HHProcessor.py')
parser.add_argument('--systematics', default=None)
parser.add_argument('--nproc', type=int, default=5)
parser.add_argument('--queue', default='short')
parser.add_argument('--output-path', default='ntuples/hadhad')
parser.add_argument('--db', default='datasets_hh')
parser.add_argument('--nice', type=int, default=10)
parser.add_argument('--nominal-only', action='store_true', default=False)
parser.add_argument('--systematics-only', action='store_true', default=False)
parser.add_argument('--dry', action='store_true', default=False)
parser.add_argument('--use-ssh', dest='use_qsub', action='store_false', default=True)
parser.add_argument('samples', nargs='*', default=None)

args = parser.parse_args()

import sys
import cluster
from higgstautau import samples

hosts = cluster.get_hosts('hosts.sfu.txt')
setup = cluster.get_setup('setup.noel.sfu.txt')

if not args.systematics_only:
    # nominal values
    datasets = samples.samples('hadhad', args.samples)
    if not datasets:
        # assume raw ds names are given
        datasets = args.samples
    cluster.run(args.student,
                db=args.db,
                datasets=datasets,
                hosts=hosts,
                nproc=args.nproc,
                nice=args.nice,
                setup=setup,
                output_path=args.output_path,
                use_qsub=args.use_qsub,
                qsub_queue=args.queue,
                dry_run=args.dry,
                separate_student_output=True)

if not args.nominal_only:
    if args.systematics is not None:
        args.systematics = [
                set(s.upper().split('+')) for s in
                args.systematics.split(',')]
    # systematics
    for datasets, systematics in samples.iter_samples('hadhad', args.samples,
            systematics=True):
        cluster.run_systematics_new('HADHAD',
                    args.student,
                    db=args.db,
                    systematics=systematics,
                    filter_systematics=args.systematics,
                    datasets=datasets,
                    hosts=hosts,
                    nproc=args.nproc,
                    nice=args.nice,
                    setup=setup,
                    output_path=args.output_path,
                    use_qsub=args.use_qsub,
                    qsub_queue=args.queue,
                    dry_run=args.dry,
                    separate_student_output=True)
