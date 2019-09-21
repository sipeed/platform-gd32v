import sys
from os.path import join

from SCons.Script import (ARGUMENTS, COMMAND_LINE_TARGETS, AlwaysBuild,
                          Default, DefaultEnvironment)


env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()

env.Replace(
    AR="riscv-nuclei-elf-gcc-ar",
    AS="riscv-nuclei-elf-as",
    CC="riscv-nuclei-elf-gcc",
    GDB="riscv-nuclei-elf-gdb",
    CXX="riscv-nuclei-elf-g++",
    OBJCOPY="riscv-nuclei-elf-objcopy",
    RANLIB="riscv-nuclei-elf-gcc-ranlib",
    SIZETOOL="riscv-nuclei-elf-size",

    ARFLAGS=["rc"],

    SIZEPRINTCMD='$SIZETOOL -d $SOURCES',

    PROGSUFFIX=".elf"
)

# Allow user to override via pre:script
if env.get("PROGNAME", "program") == "program":
    env.Replace(PROGNAME="firmware")

env.Append(
    BUILDERS=dict(
        ElfToBin=Builder(
            action=env.VerboseAction(" ".join([
                "$OBJCOPY",
                "-O",
                "binary",
                "$SOURCES",
                "$TARGET"
            ]), "Building $TARGET"),
            suffix=".bin"
        ),
        ElfToHex=Builder(
            action=env.VerboseAction(" ".join([
                "$OBJCOPY",
                "-O",
                "ihex",
                "$SOURCES",
                "$TARGET"
            ]), "Building $TARGET"),
            suffix=".hex"
        )
    )
)

if not env.get("PIOFRAMEWORK"):
    env.SConscript("frameworks/_bare.py", exports="env")

#
# Target: Build executable and linkable firmware
#

target_elf = None
if "nobuild" in COMMAND_LINE_TARGETS:
    target_elf = join("$BUILD_DIR", "${PROGNAME}.elf")
    target_firm = join("$BUILD_DIR", "${PROGNAME}.bin")
    target_hex = join("$BUILD_DIR", "${PROGNAME}.hex")
else:
    target_elf = env.BuildProgram()
    target_firm = env.ElfToBin(join("$BUILD_DIR", "${PROGNAME}"), target_elf)
    target_hex = env.ElfToHex(join("$BUILD_DIR", "${PROGNAME}"), target_elf)

AlwaysBuild(env.Alias("nobuild", target_firm))
target_buildprog = env.Alias("buildprog", target_firm, target_firm)
#target_buildhex = env.Alias("buildhex", target_hex, target_hex)

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
debug_tools = board.get("debug.tools", {})
upload_source = target_firm
upload_actions = []

if upload_protocol == "serial":
    # def __configure_upload_port(env):
    #     return basename(env.subst("$UPLOAD_PORT"))

    env.Replace(
        # __configure_upload_port=__configure_upload_port,
        UPLOADER="stm32flash",
        UPLOADERFLAGS=[
            "-g", board.get("upload.offset_address", "0x08000000"),
            "-b", "115200", "-w"
        ],
        #UPLOADCMD='$UPLOADER $UPLOADERFLAGS "$SOURCE" "${__configure_upload_port(__env__)}"'
        UPLOADCMD='$UPLOADER $UPLOADERFLAGS "$SOURCE" "$UPLOAD_PORT"'
    )

    upload_actions = [
        env.VerboseAction(env.AutodetectUploadPort, "Looking for upload port..."),
        env.VerboseAction("$UPLOADCMD", "Uploading $SOURCE")
    ]

elif upload_protocol == "dfu":
    hwids = board.get("build.hwids", [["0x0483", "0xDF11"]])
    vid = hwids[0][0]
    pid = hwids[0][1]
    _upload_tool = "dfu-util"
    _upload_flags = [
        "-d", "%s:%s" % (vid.split('x')[1], pid.split('x')[1]),
        "-a", "0", "--dfuse-address",
        "%s:leave" % board.get("upload.offset_address", "0x08000000"), "-D"
    ]
    
    upload_actions = [env.VerboseAction("$UPLOADCMD", "Uploading $SOURCE")]

    env.Replace(
        UPLOADER = _upload_tool,
        UPLOADERFLAGS = _upload_flags,
        UPLOADCMD = '$UPLOADER $UPLOADERFLAGS "${SOURCE.get_abspath()}"'
    )

    upload_source = target_firm

elif upload_protocol in debug_tools:
    openocd_args = [
        #"-c",
        #"debug_level %d" % (2 if int(ARGUMENTS.get("PIOVERBOSE", 0)) else 1),
        #"-s", platform.get_package_dir("tool-openocd-gd32v") or ""
    ]
    # openocd_args.extend([ 
    #     "-f",
    #     "scripts/temp/openocd_%s.cfg" %("gdlink" if upload_protocol == "gd-link" else "jlink")  # .cfg in a temp path
    # ])
    openocd_args.extend(
        debug_tools.get(upload_protocol).get("server").get("arguments", [])
    )
    openocd_args.extend([
        "-c", "init; halt;",
        "-c", "flash protect 0 0 last off; program {$SOURCE} verify; mww 0xe004200c 0x4b5a6978; mww 0xe0042008 0x01; resume; exit 0;"
    ])
    env.Replace(
        UPLOADER="openocd",
        UPLOADERFLAGS=openocd_args,
        UPLOADCMD="$UPLOADER $UPLOADERFLAGS")
    upload_source = target_elf
    upload_actions = [env.VerboseAction("$UPLOADCMD", "Uploading $SOURCE")]

# custom upload tool
elif upload_protocol == "custom":
    upload_actions = [env.VerboseAction("$UPLOADCMD", "Uploading $SOURCE")]

else:
    sys.stderr.write("Warning! Unknown upload protocol %s\n" % upload_protocol)

AlwaysBuild(env.Alias("upload", upload_source, upload_actions))


#
# Setup default targets
#

Default([target_buildprog, target_size])