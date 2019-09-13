from platformio.managers.platform import PlatformBase

class Gd32vPlatform(PlatformBase):

    def get_boards(self, id_=None):
        result = PlatformBase.get_boards(self, id_)
        if not result:
            return result
        if id_:
            return self._add_dynamic_options(result)
        else:
            for key, value in result.items():
                result[key] = self._add_dynamic_options(result[key])
            return result

    def _add_dynamic_options(self, board):
        # upload protocols
        if not board.get("upload.protocols", []):
            board.manifest['upload']['protocols'] = ["serial"]
        if not board.get("upload.protocol", ""):
            board.manifest['upload']['protocol'] = "serial"

        # debug tools
        debug = board.manifest.get("debug", {})
        non_debug_protocols = ["serial"]
        supported_debug_tools = [
            "jlink",
            "gd-link",
            # "ft2232",  # duplicate of sipeed-rv-debugger
            "sipeed-rv-debugger",
            "altera-usb-blaster",
            "um232h"
        ]

        upload_protocol = board.manifest.get("upload", {}).get("protocol")
        upload_protocols = board.manifest.get("upload", {}).get(
            "protocols", [])
        upload_protocols.extend(supported_debug_tools)
        if upload_protocol and upload_protocol not in upload_protocols:
            upload_protocols.append(upload_protocol)
        board.manifest['upload']['protocols'] = upload_protocols

        if "tools" not in debug:
            debug['tools'] = {}

        # Only FTDI based debug probes
        for link in upload_protocols:
            if link in non_debug_protocols or link in debug['tools']:
                continue

            if link in ["jlink", "gd-link", "altera-usb-blaster"]:
                openocd_interface = link
            else:
                openocd_interface = "ftdi/" + link

            server_args = [
                "-s", "$PACKAGE_DIR/share/openocd/scripts",
                "-f", "interface/%s.cfg" % openocd_interface,
                "-c", "transport select jtag",
                "-f", "target/gd32vf103.cfg"
            ]
            server_args.append("-c")
            if link in ["um232h"]:
                server_args.append("adapter_khz 8000")
            else:
                server_args.append("adapter_khz 1000")

            debug['tools'][link] = {
                "server": {
                    "package": "tool-openocd-gd32v",
                    "executable": "bin/openocd",
                    "arguments": server_args
                }
            }

        board.manifest['debug'] =debug
        return board
