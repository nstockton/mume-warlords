# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


# Future Modules:
from __future__ import annotations

# Built-in Modules:
import os
import warnings


RE_DIR_SEP: str = rf"\x{ord(os.sep):x}"
warnings.filterwarnings(
	"ignore",
	category=SyntaxWarning,
	module=RE_DIR_SEP.join([r".*", "magic", "magic$"]),
)
