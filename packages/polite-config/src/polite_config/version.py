#    Copyright (C) 2014-2019 Donald Stufft and individual contributors
#    Copyright (C) 2021-2024 Mathew Topper

import packaging.version as version


class Version(version.Version):
    @property
    def major(self) -> int:
        return self.release[0] if len(self.release) >= 1 else 0

    @property
    def minor(self) -> int:
        return self.release[1] if len(self.release) >= 2 else 0

    @property
    def micro(self) -> int:
        return self.release[2] if len(self.release) >= 3 else 0
