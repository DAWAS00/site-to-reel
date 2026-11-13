# Capture

## Rules

- **Capture the local dev site the user already runs.** In the example that was `http://127.0.0.1:4321`. Never stop or restart it without the user's approval.
- **Use a clean in-memory playwright-cli session.** It has no profile, so it holds none of the user's data. Use `reducedMotion: reduce` so captures settle.
- **Read-only first.** Run `tools/survey.js` for headings, links, buttons, inputs and images with their page-y positions, plus the localStorage keys. Choose scroll positions and targets from that output.
- **Real states only.** To show a change, click the real control and capture the result: Save becomes Saved, Copy becomes Copied, the header count goes up. Don't draw toasts or counts.
- **Demo data.**
  - Create at most the one item the film needs, such as a single bookmark.
  - Record storage before, after the demo, and after restoring, and return all three.
  - Restore exactly the "before" state: remove keys you added and put back the original values.
  - In the example, storage was `[]` before and `[]` after.
- **Never submit forms**, sign in, or touch flows the brief rules out (in the example, a Contribute flow).
- **Use the public domain on screen.** Captures may show the local site, but text the film adds always uses `brand.publicUrl`.

## Scale

- `cli3x.config.json`: 540×960 css at device scale 3, which gives 1620×2880 PNGs. The camera can hold z ≤ 3 with no upscaling.
- `cli4x.config.json`: the same at 4x (2160×3840). Use it for one tiny detail you need to hold larger. In the example, a 10 px "1 resource on your shelf" was held at z 4, about 40 px in frame.
- If the film needs a result that isn't in the first viewport, capture the same search scrolled to it. Don't jump to a different item than the one the camera just showed. The critic caught exactly this: the film zoomed in on "Noiced" and then opened "Phosphor Icons".

## Boxes

`tools/capture.js` returns `{caps: {<shot>: {url, scrollY, boxes: {<name>: {x, y, w, h, text}}}}}`. Boxes are in css px relative to the shot's scroll position. Save `{"caps": …}` as `capture3x/boxes.json`. Callouts then refer to them as `"box": "<shot>.<name>"`.

To find an element, `find({sel, re})` picks the topmost visible element matching a CSS selector and a case-insensitive text regex, choosing the smallest on ties. Add a one-off box later with a small script (see `examples/dawas-shlef/tools/boxes-extra.js`), or use a literal `rect`.

## Previews for scatter cards

Use real site preview images (the ones the site itself shows) placed on native paper cards. Don't use made-up thumbnails.

## Example scripts

`examples/dawas-shlef/tools/` contains:
- `capture3x.js`: 12 states, including real Save and Copy clicks.
- `capture-library-phosphor.js`: a scrolled search result.
- `capture-shelf4x.js`: a 4x detail capture, with a bookmark created and removed.
- `boxes-extra.js` and `survey.js`.
