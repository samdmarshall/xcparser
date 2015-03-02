import os
import sys
import subprocess
from subprocess import CalledProcessError

import CoreFoundation

class xcrun(object):
    """
    This class exists to execute 'xcrun' tools.
    """
    
    @classmethod
    def BuildLocation(cls, project, sym_root):
        build_dir_path = '';
        default_dd_path = os.path.expanduser("~/Library/Developer/Xcode/DerivedData/");
        relative_dd_path = False;
        derived_data = CoreFoundation.CFPreferencesCopyAppValue('IDECustomDerivedDataLocation', 'com.apple.dt.Xcode');
        if derived_data == None:
            derived_data = default_dd_path;
        else:
            if derived_data[0] != '/':
                derived_data = os.path.join(project.path, derived_data);
        
        location_style = CoreFoundation.CFPreferencesCopyAppValue('IDEBuildLocationStyle', 'com.apple.dt.Xcode');
        if location_style == 'Unique':
            # this needs to be generated
            unique_path = '';
            build_dir_path = os.path.join(derived_data, unique_path);
        elif location_style == 'Shared':
            shared_path = CoreFoundation.CFPreferencesCopyAppValue('IDESharedBuildFolderName', 'com.apple.dt.Xcode');
            build_dir_path = os.path.join(derived_data, shared_path);
        elif location_style == 'Custom':
            location_type = CoreFoundation.CFPreferencesCopyAppValue('IDECustomBuildLocationType', 'com.apple.dt.Xcode');
            custom_path = CoreFoundation.CFPreferencesCopyAppValue('IDECustomBuildProductsPath', 'com.apple.dt.Xcode');
            if location_type == 'RelativeToDerivedData':
                build_dir_path = os.path.join(derived_data, custom_path);
            elif location_type == 'RelativeToWorkspace':
                build_dir_path = os.path.join(project.path.base_path, custom_path);
            elif location_type == 'Absolute':
                build_dir_path = custom_path;
        elif location_style == 'DeterminedByTargets':
            build_dir_path = os.path.join(project.projectRoot.obj_path, sym_root);
        
        return build_dir_path;
    
    @classmethod
    def resolvePathFromLocation(cls, location_string, path, base_path):
        path_type, item_path = location_string.split(':');
        if path_type == 'group':
            return os.path.join(path, item_path);
        elif path_type == 'absolute':
            return item_path;
        elif path_type == 'developer':
            return os.path.join(resolve_developer_path(), item_path);
        elif path_type == 'container':
            return os.path.join(base_path, item_path);
        else:
            print 'Invalid item path name!';
            return item_path;
    
    @classmethod
    def make_subprocess_call(cls, call_args, shell_state=False):
        error = 0;
        output = '';
        try:
            output = subprocess.check_output(call_args, shell=shell_state);
            error = 0;
        except CalledProcessError as e:
            output = e.output;
            error = e.returncode;
        return (output, error);
    
    @classmethod
    def resolve_sdk_path(cls, sdk_name):
        xcrun_result = xcrun.make_subprocess_call(('xcrun', '--show-sdk-path', '--sdk', sdk_name));
        if xcrun_result[1] != 0:
            print 'Please run Xcode first!';
            sys.exit();
        sdk_path = xcrun_result[0].rstrip('\n');
        return sdk_path;
    
    @classmethod
    def resolve_developer_path(cls):
        platform_path = '';
        xcrun_result = xcrun.make_subprocess_call(('xcode-select', '-p'));
        if xcrun_result[1] != 0:
            print 'Please run Xcode first!';
            sys.exit();
        developer_path = xcrun_result[0].rstrip('\n');
        return developer_path;
    
    @classmethod
    def perform_xcodebuild(cls, project, scheme_name, type, scheme_config_settings):
        build_command = 'xcodebuild -project "'+project.path.obj_path+'" -scheme "'+scheme_name+'" ';
        for item in scheme_config_settings:
            build_command+=str(item)+' ';
        build_command+=' '+type;
        result = xcrun.make_subprocess_call(build_command, True);
        print result[0];