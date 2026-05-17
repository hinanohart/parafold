# experiments/_wip — local-only failure-recovery sandbox

When a milestone hits a hard failure (build-stuck, kluster CRITICAL, ≥50% test
fail, three retries on the same error) the work-tree is `cp -r`'d into a dated
subdirectory here for later post-mortem. **Never `rm -rf` a failed work-tree.**

```
experiments/_wip/
├── README.md          (this file, tracked)
├── .gitkeep           (tracked)
└── <phase>-failed-<n>/   (ignored — local-only)
    ├── POSTMORTEM.md     (trace + tried alternatives)
    └── ...               (cp -r of the failed tree)
```

The repo `.gitignore` whitelists only `README.md` and `.gitkeep` in this
directory; everything else is local. Do not push failed work-trees to GitHub.
