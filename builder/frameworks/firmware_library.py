from os.path import isdir, join

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()

board = env.BoardConfig()

FRAMEWORK_DIR = env.PioPlatform().get_package_dir("framework-gd32vf103-sdk")
assert FRAMEWORK_DIR and isdir(FRAMEWORK_DIR)

env.SConscript("_bare.py", exports="env")

env.Append(

    CPPPATH = [
        join(FRAMEWORK_DIR, "GD32VF103_standard_peripheral"),
        join(FRAMEWORK_DIR, "GD32VF103_standard_peripheral", "Include"),
        join(FRAMEWORK_DIR, "GD32VF103_usbfs_driver"),
        join(FRAMEWORK_DIR, "GD32VF103_usbfs_driver", "Include"),
        join(FRAMEWORK_DIR, "RISCV", "drivers"),
        join(FRAMEWORK_DIR, "RISCV", "env_Eclipse"),
        join(FRAMEWORK_DIR, "RISCV", "stubs"),
    ],

    LIBS = [
        "c"
    ]

)



env.Replace(
    LDSCRIPT_PATH = join(FRAMEWORK_DIR, "RISCV", "env_Eclipse", board.get("build.ldscript")) 
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
        join("$BUILD_DIR", "RISCV"),
        join(FRAMEWORK_DIR, "RISCV")),

]

env.Prepend(LIBS=libs)

# if board.get("name") == "GD32VF103V-EVAL":
    
#     env.Prepend(
#         CPPPATH = [
#             join(FRAMEWORK_DIR, "Utilities"),
#             join(FRAMEWORK_DIR, "Utilities", "LCD_common"),
#         ]
#     )

#     libs = [
#         env.BuildLibrary(
#             join("$BUILD_DIR", "eval_board_lib"),
#             join(FRAMEWORK_DIR, "Utilities")),
#     ]

#     env.Prepend(LIBS=libs)

