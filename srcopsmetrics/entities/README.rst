====================================
Meta-information Indicators Entities
====================================

Entity Criteria
===============

See template.py for necessary functionality that has to be provided in each Entity implementation.


Meta-information Indicators Metrics
===================================

For every repository we want to gather following metrics:


Time to Close an Issue (ttci)
-----------------------------
For every closed Issue in repository.


Median Time to Close an Issue (mttci)
-----------------------------
Each Issue ttci can be compared to the metrics of Issues closed before.
Therefore, median ttci for every Issue in repository.


Time to Close an Issue Score (ttci_score)
-----------------------------
Score from "future" based on Polynomial model that fits the mttci_time data.  


Time To First Review (ttfr)
---------------------------
For every PR, extract the time of its first review.


Median Time to First Review (mttfr)
---------------------------------
Same as for mttci_time


Time To First Review Score (ttfr_score)
---------------------------
For every PR, extract the time of its first review.



