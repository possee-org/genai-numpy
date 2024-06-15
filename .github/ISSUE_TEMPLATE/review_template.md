---
name: Review
about: Create and assign a task for yourself and/or others
title: 'Review: AI Gen Examples for '
labels: review
assignees: 'bmwoodruff'

---
**Link to your fork:**

<!-- Includee a link to your fork -->




**Checks**
<!-- Make sure you have ran all the tests, and visually checked the docs look correct for each example you added.
Leave this section in place and check off each item to confirm you have ran the tests. -->

```
spin build && python -m pip install . && spin docs && python tools/refguide_check.py --doctests
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



