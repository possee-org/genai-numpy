---
name: Review
about: Submit a branch on your fork to a tech lead for review
title: 'Review: AI Gen Examples for '
labels: review
assignees: 'bmwoodruff'

---
**Link to your fork:**

<!-- Include a link to the branch on your fork that contains your committed changes. -->




**Checks**
<!-- Make sure you have ran all the tests, and visually checked the docs look correct for each example you added.
Leave this section in place and check off each item to confirm you have ran the tests. -->

```
spin build && python -m pip install . && spin docs && python tools/refguide_check.py --doctests && spin lint
```
- [ ] All tests have passed
- [ ] A visual inspection of the generated docs is correct

**Acceptance Criteria:**

<!-- Leave this section as is. It will ping @bmwoodruff. -->

Close when the following are complete, in order:
- [ ] Reviewed by @bmwoodruff
- [ ] Any suggestions to fork have been merged.
- [ ] Reviewed by Numpy Mainter:

When all tasks are complete:
- [ ] Submitted as PR to NumPy.



