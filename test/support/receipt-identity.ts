/**
 * Test preload: hash the evals source tree and the installed gbrain once per
 * test process, before any test's timer starts.
 *
 * Every receipt carries `execution.source_tree` and `execution.product`.
 * `sourceTreeIdentity` reads every tracked and untracked file (about 1.7 GB of
 * committed benchmark artifacts in October 2026) and `productIdentity` hashes
 * the gbrain package; both cache per process. Left lazy, that one-time cost
 * (about 1.6 s warm and 3.4 s with a cold page cache on a 4-core machine) fell
 * inside whichever test upgraded the first receipt. Under load it passed Bun's
 * 5 s timeout, and a timeout that landed during `git status` also cached
 * `dirty: null` for every later test in the process.
 */
import { productIdentity, sourceTreeIdentity } from '../../eval/runner/receipt.ts';

sourceTreeIdentity();
productIdentity();
