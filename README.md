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

## Weekly plans
Open the app on Sunday at or after 8 a.m. device time to preview the upcoming Monday’s plan. The draft rotates through the built-in catalog and uses the planned-food score to select five dinners alongside four rotating quick lunches. Starting the draft replaces the active menu and clears its checkmarks and coach additions. This feature runs while the app is open, including offline once the app shell is cached.

## Important current limitations
- The app still stores changes in this browser's local storage; there is no account or cross-device sync.
- Grocery prices and retailer ordering are not connected.
- Nutrient estimates use [USDA FoodData Central SR Legacy](https://fdc.nal.usda.gov/download-datasets/) food matches and approximate portions. The weekly score averages eight percentages of seven days of [FDA Daily Values](https://www.fda.gov/food/nutrition-facts-label/daily-value-nutrition-and-supplement-facts-labels), each capped at 100%. The shared reference is for comparing plans. Unmatched ingredients and unplanned meals are excluded.
- Meal photos load from Unsplash and require internet unless previously cached by the browser.
- Offline support caches the app shell; first launch and first cache setup require internet.
