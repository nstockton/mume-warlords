# Copyright (C) 2025 Nick Stockton
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Future Modules:
from __future__ import annotations


__version__: str
try:  # pragma: no cover
	from ._version import __version__
except ImportError:  # pragma: no cover
	__version__ = "0.0.0"
