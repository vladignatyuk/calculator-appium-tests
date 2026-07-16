# Samsung Calculator — Appium Test Suite

End-to-end UI test automation for the stock Samsung Calculator app
(`com.sec.android.app.popupcalculator`), built with **Appium + Python + pytest**
using the **Page Object Model**. Runs against a real Android device.

## Scope

- **Keypad**: addition, subtraction, multiplication (incl. by zero),
  division (incl. a non-terminating result), subtraction to a negative
  result, decimals, a leading decimal point, negative numbers (sign toggle,
  double toggle), percentage (standalone and within an expression, incl.
  `0%`), parentheses, repeated `=`, leading zeros, clear, backspace (incl.
  down to the last remaining digit).
- **Errors / edge cases**: divide by zero (including `0/0` and a negative
  dividend), long numbers, repeated operators, an operator pressed before any
  operand, `=` on a fully empty display, an unclosed parenthesis,
  backspace/clear on an already empty display, a doubled decimal point,
  overflow into scientific notation.
- **History**: a calculation appears in history, clearing history, entries
  stay in chronological order across multiple calculations, a repeated `=`
  adds its own entry, a failed (error) calculation is *not* recorded.
- **Unit converter**: default category/units, producing a converted value,
  decimal input, switching category tabs, negative converted values,
  backspace (incl. down to an empty field), clearing both fields.

Scientific mode is intentionally out of scope for this suite. Tests
deliberately favor equivalence-class coverage over exhaustiveness — e.g. only
2 of the converter's 5 categories are exercised, since switching category is
the same code path regardless of which one; extra categories would add
runtime without covering new behavior.

## Behavioral notes (confirmed on-device)

A few non-obvious things that shaped how the tests and page objects are
written — worth knowing before adding more:

- **History order**: `HistoryPage.get_entries()` returns rows in
  chronological order (oldest first, most recent **last**), not
  most-recent-first. Also, only currently-rendered rows are returned, so
  keep ordering assertions to a handful of entries after clearing first.
- **History panel can self-dismiss**: after `clear_history()` (or
  sometimes just after being read), the panel may already be closed by the
  time you'd call `close()`. `HistoryPage.close()` checks `is_open()` first
  to avoid pressing back once too many and exiting the app entirely.
  Likewise, opening history while it's *already* empty doesn't render the
  panel at all (no clear button to click) — see `_ensure_history_cleared()`
  in `tests/test_history.py`.
- **Failed calculations aren't recorded in history** (e.g. divide by zero).
- **Converter category selection persists** across app restarts (it's not
  reset by `terminate_app`/`activate_app`). The `converter` fixture (see
  `conftest.py`) always restores it to Area on teardown, *even if the test
  itself fails* -- restoring it only at the end of a passing test body isn't
  enough, since an assertion failure partway through would skip that line
  and leak the wrong category into every test/run afterwards.
- **Converter negative values use a typographic minus sign** (U+2212), not
  an ASCII hyphen. `extract_numeric()` normalizes it first — without that,
  a negative result silently comes back positive instead of raising.
- **`ConverterPage.active_tab_title()`**: all 5 category tabs share the
  same `TAB_TITLE` resource-id, so the selected one is identified via its
  `content-desc`, which ends with `"Selected"` (e.g. `"Temperature Tab 3 of
  9 Selected"`), rather than by grabbing the first match.

## Project structure

```
calculator-appium-tests/
├── pages/
│   ├── calculator_page.py   # keypad screen
│   ├── history_page.py      # history panel
│   └── converter_page.py    # unit converter screen
├── tests/
│   ├── test_arithmetic.py
│   ├── test_errors.py
│   ├── test_history.py
│   └── test_converter.py
├── conftest.py               # Appium session, page-object fixtures, failure artifacts hook
├── requirements.txt
├── pytest.ini
├── artifacts/                 # screenshots + page-source dumps from failed runs (generated, gitignored)
└── README.md
```

## Requirements

- macOS/Linux/Windows with Python 3.9+
- Node.js + npm
- A real Android device with USB debugging enabled, connected via USB
- Android SDK platform-tools (`adb`) and, if you need a fresh SDK, the
  command-line tools (`sdkmanager`)

## One-time setup

1. **Enable USB debugging** on the device: Settings → About phone → tap
   *Build number* 7 times → Settings → Developer options → USB debugging.

2. **Install Node.js** (if missing), then Appium and its Android driver:
   ```
   npm install -g appium
   appium driver install uiautomator2
   ```

3. **Install the Android SDK** if you don't already have one, e.g. via
   Homebrew cask, or manually via the command-line tools zip from
   https://developer.android.com/studio#command-tools. Make sure
   `ANDROID_HOME`/`ANDROID_SDK_ROOT` and `platform-tools` are on your `PATH`,
   e.g. in `~/.zshrc`:
   ```
   export ANDROID_HOME="$HOME/Library/Android/sdk"
   export ANDROID_SDK_ROOT="$ANDROID_HOME"
   export PATH="$ANDROID_HOME/platform-tools:$ANDROID_HOME/cmdline-tools/latest/bin:$PATH"
   ```

4. **Verify the device is visible:**
   ```
   adb devices
   ```
   Note the serial shown (e.g. `RZCX11XCA4T`).

5. **Point the suite at your device**, either by editing `DEVICE_UDID` in
   `conftest.py`, or without touching source via env vars:
   ```
   export CALC_DEVICE_UDID=RZCX11XCA4T
   export CALC_APPIUM_SERVER_URL=http://127.0.0.1:4723/wd/hub  # optional, this is the default
   ```

6. **Install Python dependencies:**
   ```
   pip install -r requirements.txt
   ```

## Running the tests

1. Start the Appium server (leave this running in its own terminal):
   ```
   appium --base-path /wd/hub
   ```

2. In another terminal, from the project root:
   ```
   pytest
   ```

Output goes straight to the console (pytest's default `-v` reporting via
`pytest.ini`) — no extra reporting tooling required.

### Running a subset

Tests are tagged with markers reflecting their place in the equivalence-class
/ boundary-value design (see `pytest.ini` for the definitions):

```
pytest -m smoke      # minimal set proving the app fundamentally works (~4 tests)
pytest -m negative    # invalid/unexpected-input handling (test_errors.py + a few others)
pytest -m boundary    # tests targeting an exact equivalence-class boundary
```

Markers aren't mutually exclusive -- a test can be both `negative` and
`boundary` (e.g. backspacing an already-empty display).

## Debugging a failure

Any failing test automatically saves a screenshot (`.png`) and the full UI
hierarchy dump (`.xml`, same format as `uiautomator dump`) to `artifacts/`,
named after the test and a timestamp -- see the `pytest_runtest_makereport`
hook in `conftest.py`. This is what you want when a test fails on a machine
you don't have physical access to (CI runner, teammate's setup): the
combination of "what the screen looked like" + "the exact locators and text
that were present" is usually enough to tell a real regression from a
locator that shifted on a newer OneUI version.

## Performance

The full suite runs in ~5 minutes against a real device (down from ~7.5min).
Two things account for that, both in `conftest.py`:

- **`driver` is session-scoped**, not per-test. Starting a fresh UiAutomator2
  session costs ~2-3s; per-test isolation already comes from `calculator`
  forcing a clean app relaunch (`terminate_app` + `activate_app`), so paying
  the session-startup cost 45 times over added nothing but time.
- **`FAST_SETTINGS`** lowers UiAutomator2's `waitForIdleTimeout` /
  `actionAcknowledgmentTimeout` from their multi-second defaults to 200ms.

What did *not* pan out, worth knowing before reaching for it again: pushing
those same settings to 0 (skip the idle check entirely) is another ~5x
faster on top of that, but reliably drops taps under a 25+ rep stress test
of a real interaction sequence — there's no safe middle ground between "full
idle wait" and "no idle wait at all" for this app, so 200ms is the floor.

Real parallelism (pytest-xdist etc.) isn't an option here: every test drives
the same physical device, which only one Appium session can control at a
time. Scaling further would need multiple physical devices, one Appium
server per device, and splitting the suite across them.

## Notes on device-specific locators

All `resource-id`s used in the Page Objects were captured directly from a
Samsung Galaxy A54 (OneUI) via:
```
adb shell uiautomator dump /sdcard/window_dump.xml
adb pull /sdcard/window_dump.xml .
cat window_dump.xml | grep -oE 'resource-id="[^"]*"' | sort -u
```
Samsung's accessibility layer wraps displayed values with extra wording (e.g.
"10 Calculation result", "Minus 2 Calculation result", "Calculator input
field 12"). `pages/calculator_page.py` normalizes this via
`normalize_display_text()` before any assertion compares it.

If you run this on a different Samsung OneUI version, some IDs, wording, or
default converter units may differ — re-run the dump above on the relevant
screen and adjust the constants in `pages/*.py` or the assertions in
`tests/*.py` accordingly.
