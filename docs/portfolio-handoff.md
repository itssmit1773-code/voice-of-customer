# Portfolio website handoff

**Title:** AI-Powered Voice of Customer & Product Prioritization  
**Slug:** ai-voice-of-customer  
**Tools:** Python · SQLite · Streamlit · NLP taxonomy · RICE · PRD  
**Project type:** Independent portfolio simulation

**Card copy**

I built a feedback analysis workflow for a fictional global SaaS product. It deduplicates support tickets, in-app reports and reviews, checks an offline text classifier, and converts the evidence into a ranked product roadmap. The highest-ranked proposal includes a PRD for recovering stalled approvals.

**Detail page copy**

Which product problem deserves the next prototype? I traced 3,933 simulated feedback events to 3,510 canonical reports and used the latest quarter for prioritization. Approval handoffs accounted for 25.3% of that quarter's reports and led the base RICE ranking. A stress test showed where a notification digest could overtake it. I proposed testing approval recovery with a measurable outcome and safety checks before allocating delivery capacity.

**Website assets**

Use `docs/dashboard.png` as the project image, with alt text “Voice of Customer dashboard showing simulated feedback counts, theme shares and monthly trends.” Link to the repository and deep-link to the case study and PRD. Link to a live app after hosting is configured. For a local review, the README has the launch steps.

## Interview walkthrough

1. **What decision was at stake?** The PM had one slot for a prototype. I wanted the roadmap to survive questions about duplicated reports, who actually complained, and what the proposed feature would address.
2. **Why count people and reports separately?** Reports show the mix of incoming feedback. A person can report the same problem several times. Distinct known users give a reach proxy, and anonymous reports remain visible in volume and accounts.
3. **Why use rules after training a model?** On the 24-case audit, the taxonomy had stronger macro F1 than the tiny Naive Bayes benchmark. It was easier to inspect and routed unclear examples to review. Four topic abstentions and the scripted corpus are limits I would address before using it with customer data.
4. **Why start with a prototype?** Approval scored 144.1 at base, but notifications can pass it under plausible joint changes. I would verify solution eligibility, obtain delivery estimates, and measure the recovery baseline before committing.
5. **How does this differ from the other portfolio projects?** This case turns qualitative evidence into a product investment decision and requirements. The growth case studies behavior and experimentation. The support automation case evaluates operational feasibility, risk and ROI.

Present this as a simulated independent project. The business metrics are demonstration results and the proposed feature has no observed rollout impact.
