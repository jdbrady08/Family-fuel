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
Open the app on Sunday at or after 8 a.m. device time to preview the upcoming Monday’s plan. The draft rotates through the built-in catalog and uses the planned-food score to select five dinners alongside four rotating quick lunches. The built-in library contains 28 dinners and 28 lunches. Newly saved imports are queued oldest first for the next draft’s dinner slots. The queue advances when you start that draft, and any extra imports carry over. Starting the draft replaces the active menu and clears its checkmarks and coach additions. This feature runs while the app is open, including offline once the app shell is cached.

## Imports and history
The Recipes tab imports public recipe pages with Recipe JSON-LD and Pinterest Pins that expose an original recipe link. Review the original quantities and serving count before saving. Imported dinners link back to the publisher for the method. When a publisher supplies a recipe photo, its URL is saved with the recipe. Photos load from the publisher while online. Open a previously saved recipe and choose Get recipe photo to retrieve one. Imported dinners use publisher protein and fiber when available and estimate the remaining tracked nutrients from matched ingredients, measured amounts, and USDA SR Legacy food data. Nutrition is recalculated for existing saved imports on opening the updated app. Recipe details list unmatched ingredients and household portion assumptions. The estimate covers the matched portion of each recipe. Library entries and history stay in this browser.

Starting a new plan records the outgoing week’s score and nutrient coverage in History. Week-to-week score changes use the nutrients measured in both plans. The coach shows the top three remaining food additions from a built-in catalog of 28 options and reranks them as you add, dismiss, or restore suggestions. The planner gives extra weight to nutrients that were among the three lowest in at least two recent plans with comparable data.

The import API runs separately on Render as `family-fuel-recipe-import`, using `python3 recipe_import.py` and the `/health` endpoint. The existing app remains on the static site. Imports need internet access.

## Lunch nutrition and healthy additions
Each fast lunch has estimated per-serving calories, protein, carbohydrate, fiber, fat, sodium and tracked vitamins and minerals. Healthy additions are paired to a chosen dinner or lunch, appear with that recipe, and contribute to its nutrition. The coach lets you change the pairing. Lunch shopping requirements scale to four servings while weekly coverage retains the average lunch attendance assumption of 3.5 people.

## Dinner sides
Each dinner supports common vegetable, bean and grain sides. The Add side selector previews nutrition and the projected weekly score for half, one or two portions per person. Saving adds seven servings to the shopping list. Added sides stay with that dinner slot when you swap its main dish. Sides are stored with the active plan.

## Shop the plan
Shopping Lists groups the current plan’s groceries under Walmart and Tom Thumb. Repeated ingredients share a row, with matching units summed and other measurements shown side by side. Remove items you already have and restore them from Already have. Removed items stay off exports and printed lists for the current week. You can move an item between stores, check it off, and export one store or both. Per-item Walmart links open product search. For Tom Thumb, copy the ingredient name and paste it into the retailer’s search. Prices, inventory, and carts are handled on the retailers’ sites.

## Important current limitations
- The app still stores changes in this browser's local storage; there is no account or cross-device sync.
- Grocery prices and retailer ordering are not connected.
- Nutrient estimates use [USDA FoodData Central SR Legacy](https://fdc.nal.usda.gov/download-datasets/) food matches and approximate portions. The weekly score averages 22 percentages of seven days of [FDA Daily Values](https://www.fda.gov/food/nutrition-facts-label/daily-value-nutrition-and-supplement-facts-labels), each capped at 100%. The shared reference is for comparing plans. Unmatched ingredients and unplanned meals are excluded.
- Meal photos load from Unsplash and require internet unless previously cached by the browser.
- Offline support caches the app shell; first launch and first cache setup require internet.
