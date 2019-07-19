import sys
from os.path import join

from SCons.Script import (ARGUMENTS, COMMAND_LINE_TARGETS, AlwaysBuild,
                          Default, DefaultEnvironment)


env = DefaultEnvironment()
platform = env.PioPlatform()
board_config = env.BoardConfig()

env.Replace(
    AR="riscv64-unknown-elf-gcc-ar",
    AS="riscv64-unknown-elf-as",
    CC="riscv64-unknown-elf-gcc",
    GDB="riscv64-unknown-elf-gdb",
    CXX="riscv64-unknown-elf-g++",
    OBJCOPY="riscv64-unknown-elf-objcopy",
    RANLIB="riscv64-unknown-elf-gcc-ranlib",
    SIZETOOL="riscv64-unknown-elf-size",

    ARFLAGS=["rc"],

    SIZEPRINTCMD='$SIZETOOL -d $SOURCES',

    PROGSUFFIX=".elf"
)

# Allow user to override via pre:script
if env.get("PROGNAME", "program") == "program":
    env.Replace(PROGNAME="firmware")

if not env.get("PIOFRAMEWORK"):
    env.SConscript("frameworks/_bare.py", exports="env")

#
# Target: Build executable and linkable firmware
#

target_elf = None
if "nobuild" in COMMAND_LINE_TARGETS:
    target_elf = join("$BUILD_DIR", "${PROGNAME}.elf")
else:
    target_elf = env.BuildProgram()

AlwaysBuild(env.Alias("nobuild", target_elf))
target_buildprog = env.Alias("buildprog", target_elf, target_elf)

#
# Target: Print binary size
#

target_size = env.Alias(
    "size", target_elf,
    env.VerboseAction("$SIZEPRINTCMD", "Calculating size $SOURCE"))
AlwaysBuild(target_size)


#
# Target: Upload by default .elf file
#
upload_protocol = env.subst("$UPLOAD_PROTOCOL")

upload_actions = []

if upload_protocol == "gd-link" :
    openocd_args = [
        "-c",
        "debug_level %d" % (2 if int(ARGUMENTS.get("PIOVERBOSE", 0)) else 1),
        "-s", platform.get_package_dir("tool-openocd-gd32v") or ""
    ]
    openocd_args.extend([ 
        "-f",
        "scripts/temp/openocd_gdlink.cfg"
    ])
    openocd_args.extend([
        "-c", "flash protect 0 0 last off; program {$SOURCE} %s verify; resume 0x20000000; exit;" %
        board_config.get("upload").get("flash_start", "")
    ])
    env.Replace(
        UPLOADER="openocd",
        UPLOADERFLAGS=openocd_args,
        UPLOADCMD="$UPLOADER $UPLOADERFLAGS")
    upload_actions = [env.VerboseAction("$UPLOADCMD", "Uploading $SOURCE")]

# custom upload tool
elif upload_protocol == "custom":
    upload_actions = [env.VerboseAction("$UPLOADCMD", "Uploading $SOURCE")]

else:
    sys.stderr.write("Warning! Unknown upload protocol %s\n" % upload_protocol)

AlwaysBuild(env.Alias("upload", target_elf, upload_actions))


#
# Setup default targets
#

Default([target_buildprog, target_size])