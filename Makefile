.PHONY: fonts check-fonts release specimen check-uv check-sfw check-trivy update-exclude-newer add add-dev lock upgrade sync audit

UV=uv
SFW=sfw
TRIVY=trivy
# Reject dependency versions published fewer than this many days ago.
MIN_RELEASE_AGE_DAYS=3
EXCLUDE_NEWER=$(shell date -u -v-$(MIN_RELEASE_AGE_DAYS)d +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d '-$(MIN_RELEASE_AGE_DAYS) days' +%Y-%m-%dT%H:%M:%SZ)

# Build the TTF and webfont files from the locked environment. FAMILY limits
# the build to one family (hand, caption, mark); all families are built by default.
fonts: sync
	$(UV) run --locked python build/build.py $(FAMILY)

# Rebuild and fail if the fonts in fonts/ don't match what the sources build.
# Other platforms build within floating-point noise of the committed files
# (see build/check.py), so the committed files are put back afterwards.
check-fonts: sync
	@tmp=$$(mktemp -d) && cp -R fonts "$$tmp/committed" && \
	$(UV) run --locked python build/build.py >/dev/null && \
	( cd build && $(UV) run --locked python check.py ../fonts "$$tmp/committed" ); status=$$?; \
	rm -rf fonts && mv "$$tmp/committed" fonts && rm -rf "$$tmp"; exit $$status

# Package dist/*.zip, SHA256SUMS and NOTES.md for a GitHub release. TAG, if
# given, must match the series version (e.g. make release TAG=v1.0.0).
release: check-fonts
	$(UV) run --locked python build/release.py $(TAG)

specimen: fonts
	@echo "Open http://localhost:8000/ (each family has a specimen page)"
	$(UV) run --locked python -m http.server 8000

check-uv:
	@command -v $(UV) >/dev/null 2>&1 || { echo "uv is required - see README.md#prerequisites"; exit 1; }

check-sfw:
	@command -v $(SFW) >/dev/null 2>&1 || { echo "Socket Firewall (sfw) is required before touching dependencies - see README.md#prerequisites"; exit 1; }

check-trivy:
	@command -v $(TRIVY) >/dev/null 2>&1 || { echo "Trivy is required - install it with 'brew install trivy' (see README.md)"; exit 1; }

# Refresh the exclude-newer cutoff stored in pyproject.toml. uv reads this
# from the file itself (not a CLI flag) so the value `uv lock` resolves with
# and the value `uv sync --locked` checks against always match.
update-exclude-newer:
	sed -i.bak 's/^exclude-newer = .*/exclude-newer = "$(EXCLUDE_NEWER)"/' pyproject.toml && rm -f pyproject.toml.bak

# PKG must pin an exact version - `uv add <pkg>` with no version writes a
# `>=` range by default, which would silently violate the exact-version
# policy.
add: check-uv check-sfw update-exclude-newer
	@echo "$(PKG)" | grep -q '==' || { echo "PKG must pin an exact version, e.g. make add PKG=fonttools==4.67.0"; exit 1; }
	$(SFW) $(UV) add "$(PKG)"

add-dev: check-uv check-sfw update-exclude-newer
	@echo "$(PKG)" | grep -q '==' || { echo "PKG must pin an exact version, e.g. make add-dev PKG=pillow==13.0.0"; exit 1; }
	$(SFW) $(UV) add --dev "$(PKG)"

# Re-resolve uv.lock. Every new/updated version must be at least
# MIN_RELEASE_AGE_DAYS old, and sfw vets each candidate before it can land
# in the lockfile. Run this whenever pyproject.toml dependencies change.
lock: check-uv check-sfw update-exclude-newer
	$(SFW) $(UV) lock

# Bump a single package in uv.lock (typically a transitive dependency with a
# known vulnerability) without touching pyproject.toml or any other locked
# version. PKG is a bare name (newest version allowed by the cutoff and the
# dependents' ranges) or an exact pin, e.g. make upgrade PKG=brotli==1.2.1.
upgrade: check-uv check-sfw update-exclude-newer
	@test -n "$(PKG)" || { echo "PKG is required, e.g. make upgrade PKG=brotli"; exit 1; }
	$(SFW) $(UV) lock --upgrade-package "$(PKG)"

# Install dependencies straight from the committed, hash-locked uv.lock.
# --locked fails instead of silently re-resolving if the lock is stale, and
# no-build in pyproject.toml blocks any third-party sdist build.
sync: check-uv
	$(UV) sync --locked

# Scan locked dependencies for HIGH-severity known vulnerabilities
audit: check-uv check-trivy
	@dir=$$(mktemp -d) && trap 'rm -rf "$$dir"' EXIT && \
	$(UV) export --format requirements.txt --no-hashes --no-emit-project -o "$$dir/requirements.txt" && \
	$(TRIVY) fs --scanners vuln --severity HIGH --exit-code 1 "$$dir/requirements.txt"
