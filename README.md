# GigaDevice GD32V: development platform for [PlatformIO](https://platformio.org)

[![Build Status](https://github.com/sipeed/platform-gd32v/workflows/Examples/badge.svg)](https://github.com/sipeed/platform-gd32v/actions)

# Usage

1. [Install PlatformIO](https://platformio.org)
2. Create PlatformIO project and configure a platform option in [platformio.ini](https://docs.platformio.org/page/projectconf.html) file:

## Stable version

```ini
[env:stable]
platform = gd32v
board = ...
...
```

## Development version

```ini
[env:development]
platform = https://github.com/sipeed/platform-gd32v.git
board = ...
...
```

# Configuration

Please navigate to [documentation](https://docs.platformio.org/page/platforms/gd32v.html).
