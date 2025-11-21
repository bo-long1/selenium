"""Runner for Behave features with single or parallel execution and Allure integration.

Runs one behave process per scenario (creates temporary single-scenario feature
files), writes Allure results per-process, merges results and optionally calls
Allure CLI to generate an HTML report.
"""
from pathlib import Path
import tempfile
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import sys
from common.utils import load_settings


def collect_scenarios(features_dir: Path):
    scenarios = []
    for feature_file in features_dir.rglob('*.feature'):
        lines = feature_file.read_text(encoding='utf-8').splitlines()
        header = []
        in_header = True
        current = None
        block = []
        for ln in lines:
            if in_header and ln.strip().startswith('Feature'):
                header.append(ln)
                in_header = False
                continue
            if in_header:
                header.append(ln)
                continue
            if ln.strip().startswith('Scenario') or ln.strip().startswith('Scenario Outline'):
                if current:
                    scenarios.append((feature_file, current, block.copy(), header.copy()))
                current = ln
                block = [ln]
            else:
                if current:
                    block.append(ln)
        if current:
            scenarios.append((feature_file, current, block.copy(), header.copy()))
    return scenarios


def write_temp_feature(tmpdir: Path, header, block, idx):
    p = tmpdir / f'scenario_{idx}.feature'
    content = []
    if header:
        content.extend(header)
    else:
        content.append('Feature: temp feature')
    content.append('')
    content.extend(block)
    p.write_text('\n'.join(content), encoding='utf-8')
    return p


def run_behave_on_feature(feature_path: Path, outdir: Path) -> int:
    # Use allure-behave formatter
    cmd = [sys.executable, '-m', 'behave', str(feature_path), '-f', 'allure_behave.formatter:AllureFormatter', '-o', str(outdir)]
    print('Running:', ' '.join(cmd))
    env = os.environ.copy()
    # ensure behave subprocess can import local packages (core, pages)
    project_root = Path(__file__).parents[1]
    prev = env.get('PYTHONPATH', '')
    if prev:
        env['PYTHONPATH'] = str(project_root) + os.pathsep + prev
    else:
        env['PYTHONPATH'] = str(project_root)
    res = subprocess.run(cmd, env=env)
    return res.returncode


def merge_allure_results(src_dirs, target_dir: Path):
    target_dir.mkdir(parents=True, exist_ok=True)
    for d in src_dirs:
        if not d.exists():
            continue
        for f in d.rglob('*'):
            if f.is_file():
                rel = f.relative_to(d)
                dest = target_dir / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, dest)


def main(argv=None):
    settings = load_settings()
    default_features = settings.get('features_dir', './features')
    features_dir = Path(default_features)
    if not features_dir.exists():
        print('Features directory not found:', features_dir)
        return 1

    mode = 'single'
    workers = os.cpu_count() or 2
    if argv and '--mode' in argv:
        try:
            mode = argv[argv.index('--mode') + 1]
        except Exception:
            pass
    if argv and '--workers' in argv:
        try:
            workers = int(argv[argv.index('--workers') + 1])
        except Exception:
            pass

    scenarios = collect_scenarios(features_dir)
    if not scenarios:
        print('No scenarios found')
        return 1

    tmp = Path(tempfile.mkdtemp(prefix='behave_tmp_'))
    print('Temp dir:', tmp)
    per_scenario_dirs = []
    feature_paths = []
    try:
        for i, (_, _, block, header) in enumerate(scenarios, start=1):
            p = write_temp_feature(tmp, header, block, i)
            feature_paths.append(p)

        result_dirs = []
        if mode == 'single':
            for i, p in enumerate(feature_paths, start=1):
                out = tmp / f'result_{i}'
                out.mkdir(parents=True, exist_ok=True)
                rc = run_behave_on_feature(p, out)
                result_dirs.append(out)
        else:
            with ThreadPoolExecutor(max_workers=workers) as ex:
                futures = {ex.submit(run_behave_on_feature, p, tmp / f'result_{i+1}'): p for i, p in enumerate(feature_paths)}
                for fut in as_completed(futures):
                    p = futures[fut]
                    try:
                        rc = fut.result()
                    except Exception as e:
                        print('Error running', p, e)
                    # collect result dir name
            # gather all result dirs
            for d in tmp.iterdir():
                if d.is_dir() and d.name.startswith('result_'):
                    result_dirs.append(d)

        # merge results into configured dir
        allure_results = Path(settings.get('allure_results_dir', './allure_results'))
        if allure_results.exists():
            shutil.rmtree(allure_results)
        merge_allure_results(result_dirs, allure_results)
        print('Allure results collected to:', allure_results)

        # try to run allure CLI to generate report
        try:
            gen_cmd = ['allure', 'generate', str(allure_results), '-o', 'allure-report', '--clean']
            print('Attempting to generate Allure HTML report (requires allure CLI)')
            subprocess.run(gen_cmd, check=True)
            print('Allure report generated at ./allure-report')
        except Exception:
            print('Allure CLI not available or failed to generate report. You can run:')
            print('allure generate', str(allure_results), '-o ./allure-report --clean')

    finally:
        try:
            shutil.rmtree(tmp)
        except Exception:
            pass

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
