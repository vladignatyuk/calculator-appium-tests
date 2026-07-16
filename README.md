# Samsung Calculator — Appium Test Suite

End-to-end UI test automation for the stock Samsung Calculator app
(`com.sec.android.app.popupcalculator`), built with **Appium + Python + pytest**
using the **Page Object Model**. Runs against a real Android device.

## Scope

- **Keypad**: addition, subtraction, multiplication, division, decimals,
  negative numbers (sign toggle, double toggle), percentage, parentheses,
  repeated `=`, leading zeros, clear, backspace.
- **Errors / edge cases**: divide by zero (including `0/0` and a negative
  dividend), long numbers, repeated operators, backspace/clear on an already
  empty display, a doubled decimal point, overflow into scientific notation.
- **History**: a calculation appears in history, clearing history, entries
  stay in chronological order across multiple calculations, a repeated `=`
  adds its own entry, a failed (error) calculation is *not* recorded.
- **Unit converter**: default category/units, producing a converted value,
  switching category tabs, negative converted values, backspace, clearing
  both fields.

Scientific mode is intentionally out of scope for this suite.

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
  reset by `terminate_app`/`activate_app`), so tests that switch category
  (e.g. to Temperature) restore it back to Area afterwards to avoid
  breaking `test_converter_default_area_units` for later runs.
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
├── conftest.py               # Appium session + CalculatorPage fixtures
├── requirements.txt
├── pytest.ini
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

5. **Set your device serial** in `conftest.py` — update `DEVICE_UDID` to match
   your own `adb devices` output.

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
