"""Command parsing and user-facing output; algorithms live in their owning modules."""
import argparse
import json
import logging
from pathlib import Path
import time

from alert_outlook.logging import configure
from alert_outlook.settings import FAMILIES, OBLAST_UIDS, Paths


def parser():
    cli = argparse.ArgumentParser(prog='alert-outlook')
    cli.add_argument('--root', type=Path, help='project directory (or ALERT_OUTLOOK_HOME)')
    cli.add_argument('--log-level', choices=['DEBUG','INFO','WARNING','ERROR'], default='INFO')
    sub = cli.add_subparsers(dest='command', required=True)
    fetch = sub.add_parser('fetch', help='pull paced, resumable alerts.in.ua history')
    fetch.add_argument('--into', type=Path, help='resume this pull directory')
    for name in ('check','predict','score','history','page'):
        sub.add_parser(name)
    tune = sub.add_parser('tune', help='search one family using CHOOSE only')
    tune.add_argument('family', choices=list(FAMILIES))
    tune.add_argument('--minutes', type=float, default=45)
    sub.add_parser('train', help='fit the CHOOSE winners and publish three weights')
    evaluate = sub.add_parser('evaluate', help='score frozen forecast rows without training')
    evaluate.add_argument('--run-id', required=True)
    evaluate.add_argument('--period', choices=['choose','benchmark','holdout'], required=True)
    return cli


def dispatch(args, paths):
    if args.command == 'fetch':
        from alert_outlook.data.sources import pull_history
        print(pull_history(OBLAST_UIDS, paths.raw / 'alerts_in_ua', paths.token(), into=args.into))
    elif args.command == 'check':
        from alert_outlook.experiments.analytics import check
        run_id, metrics = check(paths)
        print(json.dumps(dict(run_id=run_id, **metrics), indent=2))
    elif args.command == 'tune':
        from alert_outlook.experiments.training import tune
        print(f'Completed configurations: {tune(paths, args.family, args.minutes)}')
    elif args.command == 'train':
        from alert_outlook.experiments.training import train
        print('Training run:', train(paths))
    elif args.command == 'evaluate':
        from alert_outlook.experiments.evaluation import evaluate
        run_id, table = evaluate(paths, args.run_id, args.period)
        print(table.to_string(index=False))
        print('Evaluation run:', run_id)
    elif args.command == 'predict':
        from alert_outlook.experiments.prediction import predict
        from alert_outlook.presentation.page import forecast_table
        from alert_outlook.data.history import names
        rows, appended = predict(paths)
        print('Data as of', rows.ts.max().tz_convert('Europe/Kyiv'))
        for family, label in FAMILIES.items():
            print('\n' + label)
            print(forecast_table(rows[rows.model == family], names(paths)).to_string())
        print('\n' + ('Logged to ' if appended else 'Already logged in ') + str(paths.predictions))
    elif args.command == 'score':
        from alert_outlook.experiments.prediction import score
        table = score(paths)
        print(table.to_string(index=False) if not table.empty else 'No logged windows have closed.')
    elif args.command == 'history':
        from alert_outlook.experiments.analytics import history
        run_id, weekly = history(paths)
        print(weekly.to_string())
        print('History run:', run_id)
    elif args.command == 'page':
        from alert_outlook.experiments.presentation import page
        print(page(paths))


def main(argv=None):
    args = parser().parse_args(argv)
    paths = Paths(args.root) if args.root else Paths()
    configure(paths, args.log_level)
    logger = logging.getLogger(__name__)
    began = time.monotonic()
    logger.info('started command', extra=dict(command=args.command, stage=args.command))
    try:
        dispatch(args, paths)
    except Exception:
        logger.exception('command failed', extra=dict(command=args.command, duration=time.monotonic() - began))
        raise SystemExit(1) from None
    logger.info('completed command', extra=dict(command=args.command, duration=time.monotonic() - began))
