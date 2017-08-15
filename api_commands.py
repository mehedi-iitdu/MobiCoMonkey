'''
api commands from python to gain information about android avds
'''
import subprocess
from typing import List
import config_reader as config
import util
from emulator import Emulator
from apk import Apk
ADB = config.adb

PRINT_FLAG = True


def adb_install_apk(emulator: Emulator, apk: Apk):
    '''
    installs provided apk to specified emulator
    '''
    util.check_file_directory_exists(apk.apk_path, True)
    try:
        result = subprocess.check_output(
            [config.adb, '-s', 'emulator-' + emulator.port, 'install', apk.apk_path]).decode()
        util.debug_print(result, flag=PRINT_FLAG)
    except subprocess.SubprocessError as error:
        print(error)
        raise ValueError("error installing.")


def adb_stop_activity_of_apk(emulator: Emulator, apk: Apk):
    '''
    stops activity specified by the apk
    '''
    # adb shell am force-stop com.my.app.package

    emulator_name = 'emulator-' + emulator.port
    subprocess.check_output(
        [config.adb, '-s', emulator_name, 'shell', 'am', 'force-stop',
         apk.package_name])
    print("package_name: " + apk.package_name + " is stopped")


def adb_start_launcher_of_apk(emulator: Emulator, apk: Apk):
    '''
        starts the specified apk.
    '''
    # adb shell monkey -p com.android.chrome -c
    # android.intent.category.LAUNCHER 1
    emulator_name = 'emulator-' + emulator.port
    subprocess.check_output(
        [config.adb, '-s', emulator_name, 'shell', 'monkey', '-p',
         apk.package_name, '-c', 'android.intent.category.LAUNCHER', '1'])
    print("package_name: " + apk.package_name + " is started")


def adb_is_package_present(emulator: Emulator, app_package_name: str) -> int:
    '''
        returns 1 if the specified package is present.
        returns 0 if the specified package is not present.
        returns 1 if multiple entries for specified package is present.
    '''
    output = subprocess.check_output(
        [config.adb, '-s', 'emulator-' + emulator.port, 'shell', 'pm',
         'list', 'packages', '|', 'grep', app_package_name]).decode().strip().split('\r\n')
    # util.debug_print(output, len(output), flag=PRINT_FLAG)
    # self.number_of_events = number_of_events
    # self.seed = seed
    if len(output) < 1:
        return 0
    elif len(output) > 1:
        return 2
    return 1


def adb_uninstall_package(emulator: Emulator, package: str):
    '''
    uninstalls the provided package if only one entry with the specified package is found.
    '''
    # if adb_is_package_present(emulator, package) is not 1:
    #     raise ValueError("Package not found / Too generic.")
    try:
        result = subprocess.check_output(
            [config.adb, '-s', 'emulator-' + emulator.port, 'uninstall', package])
        print("uninstalled " + package)
    except subprocess.SubprocessError as error:
        print("maybe not found/uninstalled already")


def adb_uninstall_apk(emulator: Emulator, apk: Apk):
    '''
    uninstalls the provided apk if installed.
    '''
    adb_uninstall_package(emulator, apk.package_name)


def adb_start_server_safe():
    '''
    checks if `adb server` is running. if not, starts it.
    '''
    try:
        status = subprocess.check_output(['pidof', ADB])
        util.debug_print('adb already running in PID: ' +
                         status.decode(), flag=PRINT_FLAG)
        return True
    except subprocess.CalledProcessError as exception:
        print('adb is not running, returned status: ' +
              str(exception.returncode))

        print('adb was not started. starting...')

        try:
            subprocess.check_output([ADB, 'start-server'])

            return True
        except subprocess.SubprocessError as exception:
            print(
                'something disastrous happened. maybe ' + ADB + ' was not found')
            return False


def adb_list_avd_devices() -> List:
    '''
    returns list of running adb_devices after formatting as a list.

        returns:
        List of adb_devices
    '''
    adb_devices = subprocess.check_output([ADB, 'devices'])
    adb_devices = adb_devices.decode().strip().split('\n')[1:]
    adb_devices_without_attached = []
    for device in adb_devices:
        adb_devices_without_attached.append(device.split('\t')[0])
    return adb_devices_without_attached


def adb_list_avd_ports() -> List[str]:
    '''
        returns:
        List of port of avd devices
    '''

    emulator_ports = []
    adb_devices = adb_list_avd_devices()
    for adb_device in adb_devices:
        emulator_port = adb_device.split('-')[1]
        if len(emulator_port) > 3:
            emulator_ports.append(emulator_port)
    return emulator_ports


def avd_model_from_pid(pid: str) -> str:
    '''
        returns:
            avd_model from `pid`
    '''
    device_details = util.ps_details_of_pid(pid)
    # print(output_raw)
    """
    PID TTY      STAT   TIME COMMAND
    15522 tty2     Rl+  128:13 /home/amit/Android/Sdk/tools/emulator64-x86 -port 5557 -avd nexus_s
    """
    device_detail = device_details.split('\n')[1:][:1][0]
    print(device_detail)
    """
    15521 tty2     Rl+  134:48 /home/amit/Android/Sdk/tools/emulator64-x86 -port 5555 -avd nexus_4
    or
    11803 ?        Sl     9:56 /home/amit/Android/Sdk/emulator/qemu/linux-x86_64/qemu-system-i386
    -port 5555     -avd Nexus6 -use-system-libs

    """
    index_of_avd = device_detail.index('-avd')
    device_model = device_detail[index_of_avd + 5:].split(' ')[0]
    """
    nexus_s
    """
    return device_model


def adb_pidof_app(emulator: Emulator, apk: Apk):
    '''
    returns PID of running apk
    '''
    try:
        result = subprocess.check_output(
            [config.adb, '-s', 'emulator-' + emulator.port, 'shell', 'pidof', apk.package_name])
        result = result.decode().split('\n')[0]
        util.debug_print(result, flag=PRINT_FLAG)
        return result
    except subprocess.SubprocessError:
        print("maybe not found/uninstalled already")


def emulator_list_of_avds():
    '''
        returns the list of possible avds by executing `emulator -list-avds`
    '''
    list_avds = subprocess.check_output([config.EMULATOR, '-list-avds'])
    return list_avds.decode().strip().split('\n')


def gradle_install(gradlew_path: str, project_path: str):
    '''
    `gradlew_path` is the full path of the gradlew inside the project folder
    '''
    util.check_file_directory_exists(gradlew_path, True)
    util.check_file_directory_exists(project_path, True)
    util.change_file_permission(gradlew_path, 555)
    print(gradlew_path, project_path)
    try:
        subprocess.check_output(
            [gradlew_path, '-p', project_path, 'tasks', 'installDebug', '--info', '--debug',
             '--stacktrace'])
    except subprocess.CalledProcessError:
        print('error: gradle problem executing: ' + gradlew_path)


def gradle_test(gradlew_path: str, project_path: str):
    '''
    `gradlew_path` is the full path of the gradlew inside the project folder
    '''
    util.check_file_directory_exists(gradlew_path, True)
    util.check_file_directory_exists(project_path, True)
    util.change_file_permission(gradlew_path, 555)
    print(gradlew_path, project_path)
    try:
        subprocess.check_output(
            [gradlew_path, '-p', project_path, 'tasks', 'connectedAndroidTest', '--info', '--debug',
             '--stacktrace'])
    except subprocess.CalledProcessError:
        print('error: gradle problem executing: ' + gradlew_path)


def main():
    '''
        main function
    '''
    devices = adb_list_avd_ports()

    print(devices)


if __name__ == '__main__':
    main()