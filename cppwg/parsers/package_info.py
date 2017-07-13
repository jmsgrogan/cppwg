import yaml

from cppwg.input.package_info import PackageInfo
from cppwg.input.module_info import ModuleInfo
from cppwg.input.class_info import CppClassInfo
from cppwg.input.free_function_info import CppFreeFunctionInfo
from cppwg.input.method_info import CppMethodInfo
from cppwg.input.variable_info import CppVariableInfo

class PackageInfoParser(object):

    def __init__(self, input_file, source_root):

        self.input_file = input_file
        self.raw_info = {}
        self.package_info = None
        self.source_root = source_root
        
    def subsititute_bool_string(self, option, input_dict, on_string="ON", off_string="OFF"):
        
        is_string = isinstance(input_dict[option], basestring)
        if is_string and input_dict[option].strip().upper() == off_string:
            input_dict[option] = False   
        elif is_string and input_dict[option].strip().upper() == on_string:
            input_dict[option] = True  
            
    def is_option_ALL(self, option, input_dict, check_string = "CPPWG_ALL"): 
         
        is_string = isinstance(input_dict[option], basestring)
        return is_string and input_dict[option].upper() == check_string
                
    def parse(self):

        with open(self.input_file, 'r') as inpfile:
            data = inpfile.read()

        self.raw_info = yaml.load(data)
        
        global_defaults = {'source_includes': [],
                           'smart_ptr_type': None,
                           'calldef_excludes': None,
                           'return_type_excludes': None,
                           'template_substitutions': [],
                           'pointer_call_policy': None,
                           'reference_call_policy': None,
                           'constructor_arg_type_excludes': None,
                           'excluded_methods': [],
                           'excluded_variables': []}

        # Parse package data
        package_defaults = {'name': 'cppwg_package',
                            'common_include_file': True,
                            'source_hpp_patterns': ["*.hpp"]}
        package_defaults.update(global_defaults)
        for eachEntry in package_defaults.keys():
            if eachEntry in self.raw_info:
                package_defaults[eachEntry] = self.raw_info[eachEntry]
        self.subsititute_bool_string('common_include_file', package_defaults)
        
        self.package_info = PackageInfo(package_defaults['name'], self.source_root, package_defaults)

        # Parse module data
        for eachModule in self.raw_info['modules']:
            module_defaults = {'name':'cppwg_module',
                               'source_locations': None,
                               'classes': [],
                               'free_functions': [],
                               'variables': [],
                               'use_all_classes': False,
                               'use_all_free_functions': False}
            module_defaults.update(global_defaults)
            
            for eachEntry in module_defaults.keys():
                if eachEntry in eachModule:
                    module_defaults[eachEntry] = eachModule[eachEntry]

            # Do classes
            class_info_collection = []
            module_defaults['use_all_classes'] = self.is_option_ALL('classes', module_defaults)
            if not module_defaults['use_all_classes']:
                for eachClass in module_defaults['classes']:
                    class_defaults = { 'name_override': None,
                                       'source_file': None}
                    class_defaults.update(global_defaults)
                    
                    for eachEntry in class_defaults.keys():
                        if eachEntry in eachClass:
                            class_defaults[eachEntry] = eachClass[eachEntry]
                    class_info = CppClassInfo(eachClass['name'], class_defaults)
                    class_info_collection.append(class_info)

            # Do functions
            function_info_collection = []
            module_defaults['use_all_free_functions'] = self.is_option_ALL('free_functions',
                                                                            module_defaults)
            if not module_defaults['use_all_free_functions']:
                for eachFunction in module_defaults['free_functions']:
                    ff_defaults = { 'name_override': None,
                                    'source_file': None}
                    ff_defaults.update(global_defaults)                    
                    function_info = CppFreeFunctionInfo(ff_defaults['name'], ff_defaults)
                    function_info_collection.append(function_info)
                    
            variable_collection = []
            use_all_variables = self.is_option_ALL('variables', module_defaults)
            if not use_all_variables:
                for eachVariable in module_defaults['variables']:
                    variable_defaults = { 'name_override': None,
                                         'source_file': None}
                    variable_defaults.update(global_defaults)                    
                    variable_info = CppFreeFunctionInfo(variable_defaults['name'], variable_defaults)
                    variable_collection.append(variable_info)            

            module_info = ModuleInfo(module_defaults['name'], module_defaults)
            module_info.class_info = class_info_collection
            module_info.free_function_info = function_info_collection
            module_info.variable_info = variable_collection
            for class_info in module_info.class_info:
                class_info.module_info = module_info
            for free_function_info in module_info.free_function_info:
                free_function_info.module_info = module_info   
            for variable_info in module_info.variable_info:
                variable_info.module_info = module_info                        
            self.package_info.module_info.append(module_info)
            module_info.package_info = self.package_info
