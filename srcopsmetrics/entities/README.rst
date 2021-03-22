====================================
Meta-information Indicators Entities
====================================

Entity Criteria
===============

See template.py for necessary functionality that has to be provided in each Entity implementation.


Meta-information Indicators Metrics
===================================
For every repository we want to gather following metrics:


Time to Close an Issue (TTCI)
-----------------------------
For every closed Issue in repository.


Median Time to Close an Issue (MTTCI)
------------------------------------------
Each Issue TTCI can be compared to the metrics of Issues closed before.
Therefore, median TTCI for every Issue in repository.


Time to Close an Issue Score (TTCI_SCORE)
-----------------------------------------
Score from "future", based on the least squares Polynomial model that fits the MTTCI data.


Time To First Review (TTFR)
---------------------------
For every PR, extract the time of its first review.


Median Time to First Review (MTFFR)
----------------------------------------
similar to MTTCI


Time To First Review Score (TTFR_SCORE)
---------------------------------------
similar to TTCI_SCORE


Time To Approve (TTA)
---------------------
Time to approve Pull Request for every PR in repository.


Median Time to Approve (MTTA)
----------------------------------
similar to MTTCI


Time To Approve Score (TTA_SCORE)
---------------------------------
similar to TTCI_SCORE


Time To Merge (TTM)
-------------------
Time to merge Pull Request for every PR.


Median Time to Merge (MTTM)
--------------------------------
similar to MTTCI


Time To Merge Score (TTM_SCORE)
-------------------------------
similar to TTCI_SCORE


Time To Respond (TTRE)
-------------------
Time for any repository contributor to respond to Issue or Pull Request.


Median Time to Respond (MTTRE)
--------------------------------
similar to MTTCI


Time To Respond Score (TTRE_SCORE)
-------------------------------
similar to TTCI_SCORE


Open/Closed Issue ratio
-----------------------


Open/Merged PullRequest ratio
------------------------------


Open/Rejected PullRequest ratio
-------------------------------


Kebechet Metrics
================

Number of Opened Issues by Manager
----------------------------------


Number of Closed Issues by Manager
----------------------------------


Number of Opened PRs by Manager
-------------------------------


Number of Closed PRs by Manager
-------------------------------


Number of Opened PRs by Manager and closed by Human
---------------------------------------------------


Open/Merged PullRequest ratio
------------------------------


Open/Rejected PullRequest ratio
-------------------------------

TODO: insert graphs for each set of scores
