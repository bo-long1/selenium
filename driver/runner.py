"""
Parallel test runner for Behave features with Allure reporting.

This module provides a clean, maintainable way to run Behave tests in parallel
or sequential mode with automatic Allure report generation.
"""
import json
import os
import shutil
import subprocess
import sys
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Tuple, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from common.utils import load_settings


class BehaveRunner:
    """Handles Behave test execution in single or parallel mode."""
    
    def __init__(self, project_root: Path):
        """Initialize runner with project root path."""
        self.project_root = project_root
        self.settings = load_settings()
        self.temp_results = Path('./temp_results')
        self.allure_results_dir = project_root / self.settings.get('allure_results_dir', 'allure_results')
    
    def run_feature(self, feature_path: Path, output_dir: Path) -> int:
        """
        Execute a single Behave feature file.
        
        Args:
            feature_path: Path to the .feature file
            output_dir: Directory to store JSON results
            
        Returns:
            Exit code (0 = success, non-zero = failure)
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / 'results.json'
        
        # Use JSON formatter for parallel execution (thread-safe)
        # JSON results are then converted to Allure format
        cmd = [
            sys.executable, '-m', 'behave',
            str(feature_path),
            '-f', 'json',
            '-o', str(output_file),
            '--no-capture'
        ]
        
        print(f'🚀 Running: {feature_path.name}')
        
        env = self._prepare_environment()
        result = subprocess.run(cmd, env=env, cwd=str(self.project_root), 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            self._log_failure(feature_path.name, result)
        
        return result.returncode
    
    def run_sequential(self, feature_files: List[Path]) -> List[Path]:
        """
        Execute features sequentially (one at a time).
        
        Args:
            feature_files: List of feature file paths
            
        Returns:
            List of result directories
        """
        result_dirs = []
        self.temp_results.mkdir(parents=True, exist_ok=True)
        
        for index, feature_path in enumerate(feature_files, start=1):
            output_dir = self.temp_results / f'result_{index}'
            self.run_feature(feature_path, output_dir)
            result_dirs.append(output_dir)
        
        return result_dirs
    
    def run_parallel(self, feature_files: List[Path], workers: int) -> List[Path]:
        """
        Execute features in parallel using multiple workers.
        
        Args:
            feature_files: List of feature file paths
            workers: Number of parallel workers
            
        Returns:
            List of result directories
        """
        self.temp_results.mkdir(parents=True, exist_ok=True)
        result_dirs = []
        
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {}
            
            for index, feature_path in enumerate(feature_files):
                output_dir = self.temp_results / f'result_{index + 1}'
                output_dir.mkdir(parents=True, exist_ok=True)
                future = executor.submit(self.run_feature, feature_path, output_dir)
                futures[future] = (feature_path, output_dir)
            
            for future in as_completed(futures):
                feature_path, output_dir = futures[future]
                try:
                    future.result()
                    result_dirs.append(output_dir)
                except Exception as error:
                    print(f'❌ Error running {feature_path.name}: {error}')
        
        return result_dirs
    
    def _prepare_environment(self) -> dict:
        """Prepare environment variables for subprocess."""
        env = os.environ.copy()
        pythonpath = env.get('PYTHONPATH', '')
        env['PYTHONPATH'] = (
            f"{self.project_root}{os.pathsep}{pythonpath}" 
            if pythonpath else str(self.project_root)
        )
        return env
    
    @staticmethod
    def _log_failure(feature_name: str, result: subprocess.CompletedProcess):
        """Log failure details from subprocess result."""
        print(f'⚠️  {feature_name} - exit code: {result.returncode}')
        if result.stderr:
            print(f'   stderr: {result.stderr[:500]}')
        if result.stdout:
            print(f'   stdout: {result.stdout[:500]}')


class AllureConverter:
    """Converts Behave JSON results to Allure format."""
    
    @staticmethod
    def convert_results(json_results_dir: Path, allure_dir: Path) -> int:
        """
        Convert all Behave JSON files to Allure format.
        
        Args:
            json_results_dir: Directory containing Behave JSON results
            allure_dir: Output directory for Allure results
            
        Returns:
            Number of scenarios converted
        """
        allure_dir.mkdir(parents=True, exist_ok=True)
        print('📝 Converting Behave JSON to Allure format...')
        
        converted_count = 0
        
        for json_file in json_results_dir.glob('**/*.json'):
            try:
                scenarios = AllureConverter._process_json_file(json_file)
                for scenario in scenarios:
                    AllureConverter._write_allure_result(scenario, allure_dir)
                    converted_count += 1
                    print(f'✅ Converted: {scenario["name"]}')
            except Exception as e:
                print(f'⚠️  Could not convert {json_file.name}: {e}')
        
        return converted_count
    
    @staticmethod
    def _process_json_file(json_file: Path) -> List[dict]:
        """Process a single Behave JSON file and extract scenarios."""
        with open(json_file, 'r', encoding='utf-8') as f:
            features = json.load(f)
        
        if not isinstance(features, list):
            return []
        
        scenarios = []
        
        for feature in features:
            feature_name = feature.get('name', 'Feature')
            
            for element in feature.get('elements', []):
                if element.get('type') == 'background':
                    continue
                
                scenario = AllureConverter._build_allure_scenario(element, feature_name)
                scenarios.append(scenario)
        
        return scenarios
    
    @staticmethod
    def _build_allure_scenario(element: dict, feature_name: str) -> dict:
        """Build Allure scenario structure from Behave element."""
        scenario_name = element.get('name', 'Scenario')
        
        steps = []
        total_duration = 0
        scenario_status = 'passed'
        error_message = None
        error_trace = None
        
        for step in element.get('steps', []):
            step_data, step_error = AllureConverter._build_allure_step(step)
            steps.append(step_data)
            total_duration += step_data.get('stop', 0)
            
            # If any step failed/errored, scenario fails
            if step_data['status'] in ['failed', 'broken']:
                scenario_status = step_data['status']
                if step_error:
                    error_message = step_error.get('message')
                    error_trace = step_error.get('trace')
        
        # Also check element-level status
        element_status = element.get('status', '')
        if element_status in ['failed', 'error']:
            scenario_status = 'failed' if element_status == 'failed' else 'broken'
        
        result = {
            'uuid': str(uuid.uuid4()),
            'name': scenario_name,
            'fullName': f'{feature_name}.{scenario_name}',
            'status': scenario_status,
            'start': 0,
            'stop': total_duration,
            'duration': total_duration,
            'steps': steps,
            'labels': AllureConverter._build_labels(feature_name, element.get('tags', []))
        }
        
        # Add error details if failed
        if error_message or error_trace:
            result['statusDetails'] = {}
            if error_message:
                result['statusDetails']['message'] = error_message
            if error_trace:
                result['statusDetails']['trace'] = error_trace
        
        return result
    
    @staticmethod
    def _build_allure_step(step: dict) -> tuple:
        """Build Allure step structure from Behave step."""
        step_result = step.get('result', {})
        raw_status = step_result.get('status', 'passed')
        step_status = AllureConverter._normalize_status(raw_status)
        step_duration = int((step_result.get('duration', 0) or 0) * 1000)
        
        step_data = {
            'name': step.get('keyword', '') + step.get('name', ''),
            'status': step_status,
            'start': 0,
            'stop': step_duration,
        }
        
        # Capture error details
        error_info = None
        if raw_status in ['failed', 'error']:
            raw_error = step_result.get('error_message', '')
            # Convert list to string if needed
            if isinstance(raw_error, list):
                error_msg = '\n'.join(raw_error)
            else:
                error_msg = str(raw_error) if raw_error else ''
            
            error_info = {
                'message': error_msg,
                'trace': error_msg  # Behave puts trace in error_message
            }
            # Add status details to step
            if error_msg:
                step_data['statusDetails'] = {
                    'message': error_msg[:500],  # Truncate long messages
                    'trace': error_msg
                }
        
        return step_data, error_info
    
    @staticmethod
    def _build_labels(feature_name: str, tags: List[str]) -> List[dict]:
        """Build Allure labels from feature name and tags."""
        labels = [
            {'name': 'feature', 'value': feature_name},
            {'name': 'language', 'value': 'gherkin'},
            {'name': 'suite', 'value': feature_name}
        ]
        
        for tag in tags:
            labels.append({'name': 'tag', 'value': tag})
        
        return labels
    
    @staticmethod
    def _normalize_status(status: str) -> str:
        """Normalize Behave status to Allure status."""
        if status == 'failed':
            return 'failed'
        elif status == 'error':
            return 'broken'  # Allure uses 'broken' for errors
        elif status in ['skipped', 'undefined']:
            return 'skipped'
        return 'passed'
    
    @staticmethod
    def _write_allure_result(scenario: dict, allure_dir: Path):
        """Write Allure result to JSON file."""
        result_file = allure_dir / f"{scenario['uuid']}-result.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(scenario, f, indent=2)


class AllureReportGenerator:
    """Generates Allure HTML reports with history preservation."""
    
    @staticmethod
    def generate(allure_results_dir: Path, report_dir: str = 'allure_report') -> bool:
        """
        Generate Allure HTML report with history.
        
        Args:
            allure_results_dir: Directory containing Allure JSON results
            report_dir: Output directory for HTML report
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if allure is available
            check_result = subprocess.run(
                ['allure', '--version'], 
                capture_output=True, 
                text=True,
                shell=True  # Required for Windows to find npm global packages
            )
            
            if check_result.returncode != 0:
                raise FileNotFoundError("Allure CLI not found")
            
            # Preserve history from previous report
            AllureReportGenerator._preserve_history(allure_results_dir, report_dir)
            
            # Generate report using shell=True for Windows compatibility
            cmd = f'allure generate "{allure_results_dir}" -o "{report_dir}" --clean'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
            
            print(f'✅ Allure report generated at ./{report_dir}')
            print(f'   View report: cd {report_dir} && python -m http.server 8080')
            return True
            
        except FileNotFoundError:
            print('⚠️  Allure CLI not installed.')
            print(f'   Install: npm install -g allure-commandline')
            print(f'   Manual: allure generate {allure_results_dir} -o ./{report_dir} --clean')
            return False
            
        except subprocess.CalledProcessError as e:
            print(f'❌ Allure generation failed: {e}')
            if hasattr(e, 'stderr') and e.stderr:
                print(f'   Error: {e.stderr}')
            return False
    
    @staticmethod
    def _preserve_history(allure_results_dir: Path, report_dir: str):
        """Copy history from previous report to current results."""
        old_history = Path(report_dir) / 'history'
        if old_history.exists():
            new_history = allure_results_dir / 'history'
            shutil.copytree(old_history, new_history, dirs_exist_ok=True)


class CLIArgumentParser:
    """Parses command-line arguments for the runner."""
    
    @staticmethod
    def parse(argv: Optional[List[str]] = None) -> Tuple[str, int, Optional[str]]:
        """
        Parse CLI arguments.
        
        Args:
            argv: Command-line arguments (defaults to sys.argv[1:])
            
        Returns:
            Tuple of (mode, workers, feature_name)
        """
        argv = argv or sys.argv[1:]
        
        mode = CLIArgumentParser._get_arg(argv, '--mode', 'single')
        workers = int(CLIArgumentParser._get_arg(argv, '--workers', str(os.cpu_count() or 2)))
        feature_name = CLIArgumentParser._get_arg(argv, '--feature', None)
        
        return mode, workers, feature_name
    
    @staticmethod
    def _get_arg(argv: List[str], flag: str, default: Optional[str]) -> Optional[str]:
        """Get argument value from command line."""
        try:
            if flag in argv:
                return argv[argv.index(flag) + 1]
        except (IndexError, ValueError):
            pass
        return default


class TestExecutor:
    """Main test execution orchestrator."""
    
    def __init__(self):
        """Initialize test executor."""
        self.runner = BehaveRunner(PROJECT_ROOT)
        self.converter = AllureConverter()
        self.report_generator = AllureReportGenerator()
    
    def execute(self, argv: Optional[List[str]] = None) -> int:
        """
        Execute tests with the specified configuration.
        
        Args:
            argv: Command-line arguments
            
        Returns:
            Exit code (0 = success, 1 = failure)
        """
        # Parse arguments
        mode, workers, feature_name = CLIArgumentParser.parse(argv)
        
        # Validate and get feature files
        feature_files = self._get_feature_files(feature_name)
        if not feature_files:
            return 1
        
        # Display configuration
        self._print_configuration(mode, workers, feature_files)
        
        # Clean up old results
        self._cleanup_old_results()
        
        try:
            # Execute tests
            result_dirs = self._run_tests(mode, workers, feature_files)
            
            # Process results
            return self._process_results(result_dirs)
            
        finally:
            self._cleanup_temp_files()
    
    def _get_feature_files(self, feature_name: Optional[str]) -> List[Path]:
        """
        Get list of feature files to execute.
        
        Supports:
            - Folder name: herokuapp → features/herokuapp/*.feature
            - Relative path: herokuapp/login.feature → features/herokuapp/login.feature
            - Absolute path: /full/path/to/file.feature
        """
        features_base_dir = PROJECT_ROOT / self.runner.settings.get('features_dir', 'features')
        
        if not features_base_dir.exists():
            print(f'❌ Features directory not found: {features_base_dir}')
            return []
        
        if feature_name:
            # Check if it's a specific .feature file
            if feature_name.endswith('.feature'):
                # Remove leading ./ if present
                clean_path = feature_name.lstrip('./')
                feature_path = features_base_dir / clean_path
                
                # Also try as absolute path
                if not feature_path.exists():
                    feature_path = Path(feature_name)
                
                if feature_path.exists() and feature_path.is_file():
                    return [feature_path]
                else:
                    print(f'❌ Feature file not found: {feature_name}')
                    return []
            else:
                # It's a folder name
                features_dir = features_base_dir / feature_name
        else:
            features_dir = features_base_dir
        
        feature_files = sorted(features_dir.glob('*.feature'))
        
        if not feature_files:
            print(f'❌ No feature files found in {features_dir}')
            return []
        
        return feature_files
    
    def _print_configuration(self, mode: str, workers: int, feature_files: List[Path]):
        """Print test execution configuration."""
        print(f'📋 Total feature files: {len(feature_files)}')
        print(f'🔧 Mode: {mode} | Workers: {workers if mode == "parallel" else "N/A"}')
    
    def _cleanup_old_results(self):
        """Clean up old test results."""
        if self.runner.allure_results_dir.exists():
            shutil.rmtree(self.runner.allure_results_dir)
        
        if self.runner.temp_results.exists():
            shutil.rmtree(self.runner.temp_results)
    
    def _run_tests(self, mode: str, workers: int, feature_files: List[Path]) -> List[Path]:
        """Execute tests based on mode."""
        if mode == 'parallel':
            print(f'🚀 Running {len(feature_files)} features in parallel with {workers} workers...')
            return self.runner.run_parallel(feature_files, workers)
        else:
            print(f'🚀 Running {len(feature_files)} features sequentially...')
            return self.runner.run_sequential(feature_files)
    
    def _process_results(self, result_dirs: List[Path]) -> int:
        """Process test results and generate reports."""
        self.runner.allure_results_dir.mkdir(parents=True, exist_ok=True)
        
        # Collect JSON files from temp directories
        all_json_files = []
        for result_dir in result_dirs:
            all_json_files.extend(result_dir.glob('*.json'))
        
        print(f'📊 Collected {len(all_json_files)} JSON result files')
        
        # Convert JSON to Allure format
        if all_json_files:
            converted = self.converter.convert_results(
                self.runner.temp_results, 
                self.runner.allure_results_dir
            )
            
            if converted > 0:
                print(f'✅ Tests completed! {converted} scenarios converted')
                
                # Check auto_generate_report setting
                auto_generate = self.runner.settings.get('auto_generate_report', True)
                
                if auto_generate:
                    self.report_generator.generate(self.runner.allure_results_dir)
                else:
                    print('⚠️  auto_generate_report is disabled')
                    print('📝 To generate report manually, run: bash generate_allure_report.sh')
                
                return 0
        
        print('❌ Tests failed or no results generated')
        return 1
    
    def _cleanup_temp_files(self):
        """Clean up temporary files."""
        # Clean temp results
        if self.runner.temp_results.exists():
            shutil.rmtree(self.runner.temp_results, ignore_errors=True)
        
        # Clean allure_json_output (legacy)
        allure_json_path = Path('./allure_json_output')
        if allure_json_path.exists():
            if allure_json_path.is_file():
                allure_json_path.unlink()
            else:
                shutil.rmtree(allure_json_path, ignore_errors=True)


def main(argv: Optional[List[str]] = None) -> int:
    """
    Main entry point for the test runner.
    
    Args:
        argv: Command-line arguments (defaults to sys.argv[1:])
        
    Returns:
        Exit code (0 = success, 1 = failure)
    """
    executor = TestExecutor()
    return executor.execute(argv)


if __name__ == '__main__':
    sys.exit(main())