# Canary And Shadow Design

The experimental canary model is compared against production baselines on canary tasks. The system calculates quality and safety deltas, flags regressions, and recommends rollout, limited rollout, or no rollout.

Shadow traffic simulates production routing while scoring canary output in parallel.
