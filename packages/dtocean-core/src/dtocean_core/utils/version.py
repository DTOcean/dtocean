# -*- coding: utf-8 -*-

#    Copyright (C) 2014-2019 Donald Stufft and individual contributors
#    Copyright (C) 2021-2024 Mathew Topper
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


import packaging.version as version


class Version(version.Version):
    
    @property
    def major(self):
        # type: () -> int
        return self.release[0] if len(self.release) >= 1 else 0
    
    @property
    def minor(self):
        # type: () -> int
        return self.release[1] if len(self.release) >= 2 else 0
    
    @property
    def micro(self):
        # type: () -> int
        return self.release[2] if len(self.release) >= 3 else 0
