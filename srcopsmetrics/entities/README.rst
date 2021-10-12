====================================
Meta-information Indicators Entities
====================================

Entity Criteria
===============

See template.py for necessary functionality that has to be provided in each Entity implementation.


How to load aggregated data
===========================

Using pandas
------------

.. code-block:: console

    >>> import pandas as pd

    >>> entity_name = "TrafficPaths"
    >>> df = pd.read_json(path_or_buf=f"{path_to_entity}/{entity_name}.json", orient="records", lines=True)
    >>> df.head()
                                                    path                                              title  count  uniques                                                 id
    0                        /aicoe-aiops/ocp-ci-analysis  GitHub - aicoe-aiops/ocp-ci-analysis: Developi...    240       28  2021-10-12 13:17:16.460405_/aicoe-aiops/ocp-ci...
    1                 /aicoe-aiops/ocp-ci-analysis/issues               Issues · aicoe-aiops/ocp-ci-analysis     81        8  2021-10-12 13:17:16.460405_/aicoe-aiops/ocp-ci...
    2                  /aicoe-aiops/ocp-ci-analysis/pulls        Pull requests · aicoe-aiops/ocp-ci-analysis     78        8  2021-10-12 13:17:16.460405_/aicoe-aiops/ocp-ci...
    3   /aicoe-aiops/ocp-ci-analysis/tree/master/noteb...  ocp-ci-analysis/notebooks at master · aicoe-ai...     68       14  2021-10-12 13:17:16.460405_/aicoe-aiops/ocp-ci...
    4               /aicoe-aiops/ocp-ci-analysis/pull/405  Replaced the build id 1364869749170769920 with...     54        6  2021-10-12 13:17:16.460405_/aicoe-aiops/ocp-ci...
    5   /aicoe-aiops/ocp-ci-analysis/tree/master/noteb...  ocp-ci-analysis/notebooks/data-sources at mast...     41        7  2021-10-12 13:17:16.460405_/aicoe-aiops/ocp-ci...


Using mi modules
----------------

.. code-block:: console

    >>> from srcopsmetrics.entities.pull_request import PullRequest

    >>> full_repo_slug = "thoth-station/mi"
    >>> pr = PullRequest(full_repo_slug)

    >>> # for local data in default mi data path
    >>> data = load_previous_knowledge(is_local=True)
    >>> data.head()
                                           title                                               body size  ...   changed_files     first_review_at    first_approve_at
    id                                                                                                        ...
    97                   ⬆️ Bump rsa from 4.0 to 4.7  Bumps [rsa](https://github.com/sybrenstuvel/py...    L  ...  [Pipfile.lock]                 NaT                 NaT
    96              ⬆️ Bump pyyaml from 5.3.1 to 5.4  Bumps [pyyaml](https://github.com/yaml/pyyaml)...    L  ...  [Pipfile.lock]                 NaT                 NaT
    95                   ⬆️ Bump rsa from 4.0 to 4.1  Bumps [rsa](https://github.com/sybrenstuvel/py...    L  ...  [Pipfile.lock]                 NaT                 NaT
    94  Automatic update of dependencies by Kebechet  Kebechet has updated the depedencies to the la...    L  ...  [Pipfile.lock] 2021-03-22 08:00:14 2021-03-22 08:00:14
    93  Automatic update of dependencies by Kebechet  Kebechet has updated the depedencies to the la...    L  ...  [Pipfile.lock] 202

Any other entity is loaded in the similar way.
If you intend to load remote data from Ceph, all of the Ceph variables need to be specified (see more in Setup section).


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


Time to Close an Issue Score (TTCIS)
-----------------------------------------
Score from "future", based on the least squares Polynomial model that fits the MTTCI data.


Time To First Review (TTFR)
---------------------------
For every PR, extract the time of its first review.


Median Time to First Review (MTFFR)
----------------------------------------
similar to MTTCI


Time To First Review Score (TTFRS)
---------------------------------------
similar to TTCIS


Time To Approve (TTA)
---------------------
Time to approve Pull Request for every PR in repository.


Median Time to Approve (MTTA)
----------------------------------
similar to MTTCI


Time To Approve Score (TTAS)
---------------------------------
similar to TTCIS


Time To Merge (TTM)
-------------------
Time to merge Pull Request for every PR.


Median Time to Merge (MTTM)
--------------------------------
similar to MTTCI


Time To Merge Score (TTMS)
-------------------------------
similar to TTCIS


Time To Respond (TTRE)
-------------------
Time for any repository contributor to respond to Issue or Pull Request.


Median Time to Respond (MTTRE)
--------------------------------
similar to MTTCI


Time To Respond Score (TTRES)
-------------------------------
similar to TTCIS


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
