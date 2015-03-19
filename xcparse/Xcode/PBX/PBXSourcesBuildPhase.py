from .PBXResolver import *
from .PBX_Base_Phase import *
from ...Helpers import logging_helper
from ...Helpers import xcrun_helper
from ..BuildSystem.Environment import Environment

class PBXSourcesBuildPhase(PBX_Base_Phase):
    
    def __init__(self, lookup_func, dictionary, project, identifier):
        self.bundleid = 'com.apple.buildphase.sources';
        self.identifier = identifier;
        self.phase_type = 'Compile Sources';
        self.files = [];
        if 'buildActionMask' in dictionary.keys():
            self.buildActionMask = dictionary['buildActionMask'];
        if 'files' in dictionary.keys():
            self.files = self.parseProperty('files', lookup_func, dictionary, project, True);
        if 'runOnlyForDeploymentPostprocessing' in dictionary.keys():
            self.runOnlyForDeploymentPostprocessing = dictionary['runOnlyForDeploymentPostprocessing'];
    
    def performPhase(self, build_system, target):
        build_system.initEnvironment();
        phase_spec = build_system.getSpecForIdentifier(self.bundleid);
        print '%s Phase: %s' % (self.phase_type, phase_spec.name);
        print '* %s' % (phase_spec.contents['Description']);
        
        compiler_dict = {};
        
        # this groups files based on compiler
        for file in self.files:
            args = ();
            file_spec = build_system.getSpecForIdentifier(file.fileRef.ftype);
            compiler = build_system.getCompilerForFileReference(file.fileRef);
            logging_helper.getLogger().info('[PBXSourcesBuildPhase]: File "%s" wants Compiler "%s"' % (file, compiler));
            
            if compiler.identifier not in compiler_dict.keys():
                compiler_dict[compiler.identifier] = set();
            if compiler.identifier in compiler_dict.keys():
                compiler_dict[compiler.identifier].add(file);
        
        # this iterates over the grouped (compiler:files) key:value pairs to create the build objects for those files
        for compiler_key in compiler_dict.keys():
            compiler = build_system.getSpecForIdentifier(compiler_key);
            
            # setting up default build environments
            if 'Options' in compiler.contents.keys():
                build_system.environment.addOptions(compiler.contents['Options']);
            
            compiler_exec = '';
            if 'ExecPath' in compiler.contents.keys():
                if build_system.environment.isEnvironmentVariable(compiler.contents['ExecPath']) == True:
                    compiler_exec_results = build_system.environment.parseKey(compiler.contents['ExecPath']);
                    if compiler_exec_results[0] == True:
                        compiler_exec = xcrun_helper.make_xcrun_with_args(('-f', str(compiler_exec_results[1])));
            else:
                logging_helper.getLogger().error('[PBXSourcesBuildPhase]: No compiler executable found!');
                break;
            args += (compiler_exec,);
            
            for file in compiler_dict[compiler_key]:
                file_path = str(file.fileRef.fs_path.root_path);
                args += (file_path,)
            
            sdk_name = build_system.environment.valueForKey('SDKROOT');
            sdk_path = xcrun_helper.make_xcrun_with_args(('--sdk', sdk_name, '--show-sdk-path'));
            args += ('-sdk', sdk_path);
            
            # this is missing all the build settings, also needs output set
            
            # this is displaying the command being issued for this compiler in the build phase
            args_str = '';
            for word in args:
                args_str += word;
                args_str += ' ';
            print args_str;
            
            # this is running the compiler command
            compiler_output = xcrun_helper.make_subprocess_call(args);
            if compiler_output[1] != 0:
                logging_helper.getLogger().error('[PBXSourcesBuildPhase]: Compiler error %s' % compiler_output[0]);
        
        print '';