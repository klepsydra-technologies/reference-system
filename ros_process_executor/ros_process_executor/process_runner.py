import rclpy
from rclpy.node import Node
import argparse
import numpy as np
import tempfile
import contextlib
import os
from pathlib import Path
from ament_index_python import get_package_prefix
import subprocess
import psutil
import time
from create_base_configuration import create_base_configuration
@contextlib.contextmanager
def terminatingRos2Run(pkg, executable, rmw, env=os.environ, args=[], **kwargs):
    """
    Run the given executable (part of the given package) under the given rmw.

    The executable is automatically terminated upon exit from the context
    """
    env = env.copy()
    env['RCUTILS_CONSOLE_OUTPUT_FORMAT'] = '[{severity}] [{name}]: {message}'
    env['RMW_IMPLEMENTATION'] = rmw
    env['RCL_ASSERT_RMW_ID_MATCHES'] = rmw

    assert 'timeout' not in kwargs, ('terminatingRos2Run does not support the timeout argument;' +
                                     'use time.sleep in the with block instead')

    ros_executable = Path(get_package_prefix(pkg))/'lib'/pkg/executable
    if not os.path.isfile(ros_executable):
        ros_executable = Path(get_package_prefix(pkg))/'lib'/executable
    cmdline = f'{ros_executable} {" ".join(args)}'
    process = subprocess.Popen(cmdline,
                               shell=True,
                               env=env,
                               **kwargs)
    try:
        shellproc = psutil.Process(process.pid)
        try:
            yield process
        finally:
            if process.poll() not in (None, 0):
                # Process terminated with an error
                raise RuntimeError(f'Command "{cmdline}" terminated with error: {process.returncode}')

            # The process returned by subprocess.Popen is the shell process, not the
            # ROS process. Terminating the former will not necessarily terminate the latter.
            # Terminate all the *children* of the shell process instead.
            children = shellproc.children()
            assert len(children) <= 1
            if children:
                rosproc = children[0]
                rosproc.terminate()
    
    except psutil.NoSuchProcess:
        print("Process already finished")
def generate_trace(*args, **kwargs):
    print(args)
    print(kwargs)
    directory = kwargs['directory']
    executable = args[0]
    runtime_sec = kwargs['runtime_sec']
    rmw = kwargs['rmw']
    pkg = kwargs['pkg']
    log_directory = get_benchmark_directory(directory, executable, runtime_sec, rmw, create=True)
    #create_base_configuration(directory, executable, runtime_sec)
    logfile = log_directory/'std_output.log'
    with logfile.open('w', encoding='utf8') as logfd:
        with terminatingRos2Run(pkg, executable, rmw,
                                args=[kwargs['config']],
                                stdout=logfd,
                                text=True):
            time.sleep(runtime_sec)
def get_benchmark_directory(base_directory, executable, runtime_sec, rmw, create=False):
    """
    Return the directory to place measurements and reports for the given experiment.

    If `create` is True, the directory is created if it does not exist yet.
    """
    # Note: memory_usage.py and std_latency.py make assumptions about the directory format.
    # Do not change this without also changing these other files.
    directory = Path(base_directory)/f'{runtime_sec}s/{rmw}/{executable}/'
    if create:
        directory.mkdir(parents=True, exist_ok=True)
    return directory

def calculate_output_files(counter):
    exe = 'kpsr_ros2_executor_benchmarks_executor' # use params
    exe = 'autoware_default_custom'
    pkg_name = 'autoware_reference_system' #'kpsr_ros2_executor'
    rmw = 'rmw_cyclonedds_cpp' # use params
    arg_config = f'/home/kpsruser/kpe-ros2-core/tests/config/my_config.json' \
        if counter==-1 else f'/home/kpsruser/kpe-ros2-core/tests/config/my_config{counter}.json'
    runtime = 30
    with tempfile.TemporaryDirectory() as temp_dir_name:
            common_args = {'pkg': pkg_name, # use params
                           'directory': temp_dir_name,
                           'config': arg_config}
            generate_trace(exe, rmw=rmw, runtime_sec=runtime, **common_args)

class ProcessRunnerRoutine(Node):
    def __init__(self):
        super().__init__('routine_process_runner')
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.is_first_iteration = True
        self.counter = -1
        #self.i = 0
    def timer_callback(self):
        if self.is_first_iteration:
            calculate_output_files(self.counter)
            environment_location, stat_location, policy_location = create_base_configuration(self.counter)
            print("======First execution completed. Results:====")
            print("environment_location",environment_location)
            print("stat_location",stat_location)
            print("policy_location",policy_location)
            print("=============================================")
            self.counter+=1
            self.is_first_iteration = False
            with open('/home/kpsruser/resources/csv_out/ok', 'w'):
                pass
            return
        policyToTry = f'/home/kpsruser/kpe-ros2-core/tests/config/streaming_policy{self.counter}.json'
        print(policyToTry)
        if os.path.isfile(policyToTry+".ok"):
            calculate_output_files(self.counter)
            environment_location, stat_location, policy_location = create_base_configuration(self.counter)
            self.counter += 1
            os.remove(policyToTry+".ok")
            with open('/home/kpsruser/resources/csv_out/ok', 'w'):
                pass
        else:
            print("waiting")

def main(args=None):
    rclpy.init(args=args)

    monitor = ProcessRunnerRoutine()

    rclpy.spin(monitor)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    monitor.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

# send these three through api request and get new policy from gen algo
