# Family Fuel — installable web app bundle

## What is included
- `index.html`: your supplied Family Fuel app, with install metadata and an iPhone install-help panel.
- `manifest.webmanifest`: Home Screen app name, colors, launch behavior and icons.
- `service-worker.js`: caches the app shell for repeat/offline launches.
- `icons/`: app icons for supported browsers and iPhone Home Screen.

## Publish it
Upload the *contents* of this folder to a static web host that serves HTTPS (for example, a static site host). The public site root should serve `index.html`. Do not open `index.html` from the Files app and expect service-worker/offline installation to work.

## Add to iPhone Home Screen
1. Open the published HTTPS address in Safari.
2. Tap Share.
3. Choose Add to Home Screen.
4. Keep “Open as Web App” enabled if offered, then tap Add.

## Important current limitations
- The app still stores changes in this browser's local storage; there is no account or cross-device sync.
- Grocery prices and retailer ordering are not connected.
- Nutrient bars in this prototype are illustrative demo indicators, not calculated nutrient adequacy.
- Meal photos load from Unsplash and require internet unless previously cached by the browser.
- Offline support caches the app shell; first launch and first cache setup require internet.
