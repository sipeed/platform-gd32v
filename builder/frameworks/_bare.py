from SCons.Script import Import

Import("env")

board = env.BoardConfig()

env.Append(

    ASFLAGS = ["-x", "assembler-with-cpp"],

    CCFLAGS=[
        "-Os",
        "-Wall", 
        "-march=%s" % board.get("build.march"),
        "-mabi=%s" % board.get("build.mabi"),
        "-mcmodel=%s" % board.get("build.mcmodel"),
        "-fmessage-length=0",
        "-fsigned-char",
        "-ffunction-sections",
        "-fdata-sections",
        "-fno-common"
    ],

    CFLAGS = [
        "-std=gnu11"
    ],

    CXXFLAGS = [
        "-std=gnu++17"
    ],

    CPPDEFINES = [
        "USE_STDPERIPH_DRIVER",
        ("HXTAL_VALUE", "%sU" % board.get("build.hxtal_value"))
    ],

    LINKFLAGS=[
        "-march=%s" % board.get("build.march"),
        "-mabi=%s" % board.get("build.mabi"),
        "-mcmodel=%s" % board.get("build.mcmodel"),
        "-nostartfiles",
        "-Xlinker",
        "--gc-sections",
        "--specs=nano.specs"
        # "-Wl,--wrap=_exit",
        # "-Wl,--wrap=close",
        # "-Wl,--wrap=fatat",
        # "-Wl,--wrap=isatty",
        # "-Wl,--wrap=lseek",
        # "-Wl,--wrap=read",
        # "-Wl,--wrap=sbrk",
        # "-Wl,--wrap=stub",
        # "-Wl,--wrap=write_hex",
        # "-Wl,--wrap=write"
    ],

    LIBS=["c"]
)


# copy CCFLAGS to ASFLAGS (-x assembler-with-cpp mode)
env.Append(ASFLAGS=env.get("CCFLAGS", [])[:])
