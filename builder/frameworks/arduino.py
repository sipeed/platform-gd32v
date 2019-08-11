from os.path import isdir, join

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()

board = env.BoardConfig()

FRAMEWORK_DIR = env.PioPlatform().get_package_dir("framework-arduino-gd32v")
assert FRAMEWORK_DIR and isdir(FRAMEWORK_DIR)
SDK_DIR = join(FRAMEWORK_DIR, "cores", "arduino", "GD32VF103_Firmware_Library")

env.SConscript("_bare.py", exports="env")

env.Append(

    CPPDEFINES = [
        ("ARDUINO", 10805),
        ("ARDUINO_VARIANT", '\\"%s\\"' % env.BoardConfig().get("build.variant").replace('"', "")),
        ("ARDUINO_BOARD", '\\"%s\\"' % env.BoardConfig().get("build.board_def").replace('"', ""))
    ],
    
    CPPPATH = [
        join(FRAMEWORK_DIR, "cores", "arduino"),
        join(FRAMEWORK_DIR, "cores", "arduino", "deprecated-avr-comp"),
        join(SDK_DIR, "GD32VF103_standard_peripheral"),
        join(SDK_DIR, "GD32VF103_standard_peripheral", "Include"),
        join(SDK_DIR, "GD32VF103_usbfs_driver"),
        join(SDK_DIR, "GD32VF103_usbfs_driver", "Include"),
        join(SDK_DIR, "RISCV", "drivers"),
        join(SDK_DIR, "RISCV", "env_Eclipse"),
        join(SDK_DIR, "RISCV", "stubs"),
    ],

    LIBS = [
        "c"
    ],

    LIBSOURCE_DIRS=[
        join(FRAMEWORK_DIR, "libraries")
    ],

)

env.Replace(
    LDSCRIPT_PATH = join(SDK_DIR, "RISCV", "env_Eclipse", board.get("build.ldscript")) 
)

#
# Target: Build Core Library
#

libs = []

if "build.variant" in env.BoardConfig():
    env.Append(
        CPPPATH=[
            join(FRAMEWORK_DIR, "variants",
                 env.BoardConfig().get("build.variant"))
        ]
    )
    libs.append(env.BuildLibrary(
        join("$BUILD_DIR", "FrameworkArduinoVariant"),
        join(FRAMEWORK_DIR, "variants", env.BoardConfig().get("build.variant"))
    ))

envsafe = env.Clone()

libs.append(envsafe.BuildLibrary(
    join("$BUILD_DIR", "FrameworkArduino"),
    join(FRAMEWORK_DIR, "cores", "arduino")
))



env.Prepend(LIBS=libs)

