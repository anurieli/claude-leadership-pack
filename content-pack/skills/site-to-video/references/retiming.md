# Audio-First Retiming

When the script or voice changes mid-build, the entire timeline must re-time. **Don't rebuild from scratch.** Piecewise-remap from old beat boundaries to new ones.

## The remap function

```python
# Map old beat boundaries → new boundaries, in order.
# Each tuple: (old_start, old_end, new_start, new_end)
beats = [
    (0.0,  5.0,  0.0,  5.5),    # beat 1A
    (5.0,  10.0, 5.5,  10.98),  # beat 1B
    (10.0, 12.3, 10.98, 13.51), # beat 2
    # ...
]

def remap(t):
    for ostart, oend, nstart, nend in beats:
        if ostart <= t <= oend:
            return nstart + (t - ostart) * (nend - nstart) / (oend - ostart)
    return t
```

Then regex-find every `}, NUMBER)` pattern inside `<script>` blocks in `index.html` and apply `remap()` to the number.

## Update order (strict)

Do these in order — earlier steps invalidate later assumptions if reordered.

1. **Root `data-duration`** — match new narration length + 1–1.5s tail
2. **`<audio>` elements** — `data-duration` for narration/music, `data-start` for SFX (repositioned to new beat moments)
3. **Final `tl.set({}, {}, N)`** pad — must be ≥ root duration
4. **Caption start times** in script
5. **All beat-internal absolute timestamps** via piecewise remap

## Verification

Re-snapshot at every beat midpoint after retiming. Run `scripts/qa-snapshots.py snapshots/` to flag any beat that ended up empty (likely an off-by-one in the remap).
