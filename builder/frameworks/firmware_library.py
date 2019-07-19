from os.path import isdir, join

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()

board_config = env.BoardConfig()

FRAMEWORK_DIR = env.PioPlatform().get_package_dir("framework-gd32vf103_firmware_library")
assert FRAMEWORK_DIR and isdir(FRAMEWORK_DIR)

env.SConscript("_bare.py", exports="env")

env.Append(

    CPPPATH = [
        join(FRAMEWORK_DIR, "GD32VF103_standard_peripheral"),
        join(FRAMEWORK_DIR, "GD32VF103_standard_peripheral", "Include"),
        join(FRAMEWORK_DIR, "GD32VF103_usbfs_driver"),
        join(FRAMEWORK_DIR, "GD32VF103_usbfs_driver", "Include"),
        join(FRAMEWORK_DIR, "n22", "drivers"),
        join(FRAMEWORK_DIR, "n22", "env_Eclipse"),
        join(FRAMEWORK_DIR, "n22", "stubs"),
        join(FRAMEWORK_DIR, "n22", "drivers"),
        join(FRAMEWORK_DIR, "n22", "drivers"),
    ],

    LIBS = [
        "c"
    ]

)



env.Replace(
    LDSCRIPT_PATH = join(FRAMEWORK_DIR, "n22", "env_Eclipse", board_config.get("build.ldscript")) 
)

#
# Target: Build Core Library
#

libs = [
    env.BuildLibrary(
        join("$BUILD_DIR", "standard_peripheral"),
        join(FRAMEWORK_DIR, "GD32VF103_standard_peripheral")),

#    env.BuildLibrary(
#        join("$BUILD_DIR", "usbfs_driver"),
#        join(FRAMEWORK_DIR, "GD32VF103_usbfs_driver")),
    
    env.BuildLibrary(
        join("$BUILD_DIR", "n22"),
        join(FRAMEWORK_DIR, "n22")),

]

env.Prepend(LIBS=libs)

if board_config.get("name") == "GD32VF103V-EVAL":
    
    env.Prepend(
        CPPPATH = [
            join(FRAMEWORK_DIR, "Utilities"),
            join(FRAMEWORK_DIR, "Utilities", "LCD_common"),
        ]
    )

    libs = [
        env.BuildLibrary(
            join("$BUILD_DIR", "eval_board_lib"),
            join(FRAMEWORK_DIR, "Utilities")),
    ]

    env.Prepend(LIBS=libs)

