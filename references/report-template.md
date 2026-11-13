# Report template

## review-notes.md

```markdown
# <Brand> reel: review notes (stage N: <silent animatics | finals>)

Status: **<silent animatics, not final ads | finals with AI-generated narrator, not <creator>>**
Output folder: `<absolute path>`

## Deliverables
| File | What |

## Metadata (ffprobe on the encoded files)
| File | ffprobe |   <- codec, WxH, pix_fmt, fps, SAR, frames, duration, audio

## Structure
Scene table: id, seconds, frames, action, transition out + why. Hero t and what.

## Checks
check_timeline: errors / warnings (explain each WARN).
qa_video: every PASS/WARN/FAIL with numbers (hook px + contrast, URL px + contrast, flashes,
holds, LUFS, true peak, loudest moment, silence before peak). Explain intended WARNs.

## Independent review and the one fix round
| # | Critic finding (timecode) | Fix | Verified how |

## Decisions I made (each is one reply to reverse)
DECISION: ... because ...

## Limitations, stated plainly
Not watched in real time. Not listened to (TTS pronunciation unverified). Captions draft. ...

## Exact commands
## Decisions for you
```

## The final message to the user

1. **Lead with the state.** For example, "silent animatics, not final ads", or "finals with an AI narrator; nobody has listened yet".
2. **Files** as clickable relative links, with verified ffprobe numbers.
3. **QA results:** only measured numbers.
4. **Changes from the critic**, plus any change to something the user approved earlier, with the reason.
5. **What's not done or not verified.**
6. **Cleanup:** the demo data removed and verified, temporary servers stopped, and the user's server untouched.
7. **What you need from them next**, as one question, and don't repeat a question the UI already shows.
