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


Median Time to Close an Issue (mttci_time)
------------------------------------------
Each Issue ttci can be compared to the metrics of Issues closed before.
Therefore, median ttci for every Issue in repository.


Time to Close an Issue Score (ttci_score)
-----------------------------------------
Score from "future", based on the least squares Polynomial model that fits the mttci_time data.


Time To First Review (ttfr)
---------------------------
For every PR, extract the time of its first review.


Median Time to First Review (mttfr_time)
----------------------------------------
similar to mttci_time


Time To First Review Score (ttfr_score)
---------------------------------------
similar to ttci_score


Time To Approve (tta)
---------------------
Time to approve Pull Request for every PR in repository.


Median Time to Approve (mtta_time)
----------------------------------
similar to mttci_time


Time To Approve Score (tta_score)
---------------------------------
similar to ttci_score


Time To Merge (ttm)
-------------------
Time to merge Pull Request for every PR.


Median Time to Merge (mttm_time)
--------------------------------
similar to mttci_time


Time To Merge Score (ttm_score)
-------------------------------
similar to ttci_score


Time To Respond (ttre)
-------------------
Time for any repository contributor to respond to Issue or Pull Request.


Median Time to Respond (mttre_time)
--------------------------------
similar to mttci_time


Time To Respond Score (ttre_score)
-------------------------------
similar to ttci_score


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
