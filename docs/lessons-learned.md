# Lessons Learned

I built this project to make a specific system design problem concrete: Enterprise AI teams use multiple models, and the right model depends on task type, quality bar, cost, latency, safety, and business risk.

## What Was Hardest To Model

The hardest part was deciding how much real-world complexity to simulate without turning the repo into an unreviewable pile of fake integrations. I wanted the core workflow to be believable, but still runnable locally.

## Most Important Tradeoff

The main tradeoff was choosing deterministic local behavior over live external systems. That makes the repo easier to validate, but it means production concerns like credentials, streaming throughput, network failure, and access control are represented as design notes rather than live integrations.

## What I Would Change Next

I would add one carefully scoped production-style integration, then measure how that changes testing, observability, and failure handling.

## What This Taught Me

This project reinforced that the hard part is not only producing an output. It is making the output explainable, testable, reviewable, and safe enough for another team to operate.

## What Production Teams Would Care About

Production teams would care about ownership, SLAs, lineage, auth, monitoring, security controls, failure modes, deployment workflow, and whether the scorecards actually match business outcomes.
