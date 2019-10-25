SrcOpsMtrcs
-------------------

This repository contains functions to store knowledge for the bot,
to use the knowledge stored by the bot to evaluate some statistics.

Pre-Usage
=========

.. code-block:: console

    pipenv install --dev

Usage - Create Bot Knowledge
============================

1. In `create_bot_knowledge.py` you can modify the list of projects to be considered.

.. code-block:: console

    PROJECTS =  [
        ("performance", "thoth-station"),
        ("kebechet", "thoth-station"),
        ("user-api", "thoth-station"),
        ("graph-refresh-job", "thoth-station"),
        ("metrics-exporter", "thoth-station"),
        ("package-analyzer", "thoth-station"),
        ("notebooks", "thoth-station"),
        ("thoth-ops", "thoth-station"),
        ("storages", "thoth-station"),
        ]

`update_knowledge flag` is used to analyze repos from existing knowledge of the bot. If set to True
and the project is not known by the bot, it won't create the knowledge (aka json) for the bot.
If set to False, a new json file with the knowledge about that repository will be created.

.. code-block:: console

    GITHUB_ACCESS_TOKEN=<github_acess_token> pipenv run python3 create_bot_knowledge.py

Usage - Use Bot Knowledge
==========================

1. In `pr_reviewer.py` the list of projects is taken from `create_bot_knowledge.py`.

.. code-block:: console

    pipenv run python3 pr_reviewer.py

If there are bots in the list of contributors of your project you can add them to the list
at the beginning of the file. In this way you can receive the percentage of the work
done by humans vs bots.

.. code-block:: console

    BOTS_NAMES = [
        "sesheta",
        "dependencies[bot]",
        "dependabot[bot]",
        ]

`number_reviewer` flag is set to 2

`analyze_single_scores` flag outputs the single contributions to the final score.

`filter_contributors` flag filters contributors of the project who never reviewed.

`detailed_statistics` flag gives a social interaction between reviewer, author PR pair in terms of percentage.

`use_median` flag is to use median for the TTR, therefore it would show Median Time to Review (MTTR)

Results (plots)
================
`MTTR-in-time-<name-project>.png` --> Mean time to Review (MTTR) variation after each PR approved in time.

`MTTR-in-time-<name-project>-authors.png` --> Mean time to Review (MTTR) variation after each PR approved for each author in time.

`thoth-station-<name-project>.png` --> Time to Review (TTR) variation after each PR approved.

`thoth-station-<name-project>-authors.png` --> Time to Review (TTR) variation after each PR approved per reviwer.

Final Score for Reviewers assignment
=====================================

The final score for the selection of the reviewers, it is based on the following
contributions. (Number of reviewers is by default 2, but it can be changed)

1. Number of PR reviewed respect to total number of PR reviewed by the team.

2. Mean time to review a PR by reviewer respect to team repostiory MTTR.

3. Mean length of PR respect to minimum value of PR length for a specific label.

4. Number of commits respect to the total number of commits in the repository.

5. Time since last review compared to time from the first review of the project respect to the present time.
(Time dependent contribution)

Each of the contribution as a weight factor, to weight the single contributions.
If all weight factors are set to 1, all contributions to the final
score have the same weight.

.. code-block:: console

    k1 = 1
    k1 = 2
    k1 = 3
    k1 = 4
    k1 = 5

Example results (analyze_single_scores=False, detailed_statistics=False, filter_contributors=False)
===================================================================================================

.. code-block:: console

    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:Project                                  --> N.PR Created |N. Commits created | N. PR rev | Mean Time to Review (MTTR) |
    INFO:__main__:<source>/<project-repo>                  -->     215      |       274         |    37     |   1 day, 19:15:01.432432   |
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:
    INFO:__main__:   Author reviews    --> N. PR rev |           MTTR            |  MLenPR   | N. commits c | % Tot Commits c |    Time last rev     |  Score   |
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:contributor 1        -->    10     |  2 days, 8:36:07.200000   |  size/M   |      81      |     29.562    % | 10/06/2019, 07:37:08 |  0.1588  |
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:contributor 2        -->    18     |  2 days, 1:05:10.388889   |  size/S   |      33      |     12.044    % | 10/18/2019, 06:52:57 |  0.0994  |
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:contributor 3        -->     5     |      22:33:10.400000      |  size/S   |      3       |     1.095     % | 10/18/2019, 06:51:31 |  0.0109  |
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:contributor 4        -->     4     |      9:28:55.500000       |  size/XS  |      2       |     0.730     % | 08/13/2019, 07:35:13 |  0.0058  |
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:contributor 5        -->     0     |            n/a            |    n/a    |      2       |     0.730     % |         n/a          |   n/a    |
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:contributor 6        -->     0     |            n/a            |    n/a    |      3       |     1.095     % |         n/a          |   n/a    |
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:contributor 7        -->     0     |            n/a            |    n/a    |      10      |     3.650     % |         n/a          |   n/a    |
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:contributor 8        -->     0     |            n/a            |    n/a    |      1       |     0.365     % |         n/a          |   n/a    |
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:sesheta              -->     0     |            n/a            |    n/a    |     139      |     50.730    % |         n/a          |   n/a    |
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:Number of reviewers identified: 2
    INFO:__main__:Reviewers: ['contributor 1', 'contributor 2']
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:Human % Tot commits  --> 49.270% |
    INFO:__main__:Bot % Tot commits    --> 50.730% |

Example results (analyze_single_scores=False, detailed_statistics=False, filter_contributors=True)
===================================================================================================

.. code-block:: console

    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:Project                                  --> N.PR Created |N. Commits created | N. PR rev | Mean Time to Review (MTTR) |
    INFO:__main__:<source>/<project-repo>                  -->     215      |       274         |    37     |   1 day, 19:15:01.432432   |
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:
    INFO:__main__:   Author reviews    --> N. PR rev |           MTTR            |  MLenPR   | N. commits c | % Tot Commits c |    Time last rev     |  Score   |
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:contributor 1        -->    10     |  2 days, 8:36:07.200000   |  size/M   |      81      |     29.562    % | 10/06/2019, 07:37:08 |  0.1588  |
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:contributor 2        -->    18     |  2 days, 1:05:10.388889   |  size/S   |      33      |     12.044    % | 10/18/2019, 06:52:57 |  0.0994  |
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:contributor 3        -->     5     |      22:33:10.400000      |  size/S   |      3       |     1.095     % | 10/18/2019, 06:51:31 |  0.0109  |
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:contributor 4        -->     4     |      9:28:55.500000       |  size/XS  |      2       |     0.730     % | 08/13/2019, 07:35:13 |  0.0058  |
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:Number of reviewers identified: 2
    INFO:__main__:Reviewers: ['contributor 1', 'contributor 2']
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:Human % Tot commits  --> 49.270% |
    INFO:__main__:Bot % Tot commits    --> 50.730% |

Example results (analyze_single_scores=True, detailed_statistics=False, filter_contributors=True)
=================================================================================================

.. code-block:: console

    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:Project                                  --> N.PR Created |N. Commits created | N. PR rev | Mean Time to Review (MTTR) |
    INFO:__main__:<source>/<project-repo>                  -->     215      |       274         |    37     |   1 day, 19:15:01.432432   |
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:
    INFO:__main__:   Author reviews    --> N. PR rev |           MTTR            |  MLenPR   | N. commits c | % Tot Commits c |    Time last rev     |  Score   |
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:contributor 1        -->    10     |  2 days, 8:36:07.200000   |  size/M   |      81      |     29.562    % | 10/06/2019, 07:37:08 |  0.1588  |
    INFO:__main__:contributor 1        -->  0.2973   |          0.7641           |  1.7467   |    0.4139    |      n/a        |        0.9672        |  0.1588  |
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:contributor 2        -->    18     |  2 days, 1:05:10.388889   |  size/S   |      33      |     12.044    % | 10/18/2019, 06:52:57 |  0.0994  |
    INFO:__main__:contributor 2        -->  0.5351   |          0.8811           |  1.2667   |    0.1686    |      n/a        |        0.9875        |  0.0994  |
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:contributor 3        -->     5     |      22:33:10.400000      |  size/S   |      3       |     1.095     % | 10/18/2019, 06:51:31 |  0.0109  |
    INFO:__main__:contributor 3        -->  0.1486   |          1.9177           |  2.5200   |    0.0153    |      n/a        |        0.9871        |  0.0109  |
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:contributor 4        -->     4     |      9:28:55.500000       |  size/XS  |      2       |     0.730     % | 08/13/2019, 07:35:13 |  0.0058  |
    INFO:__main__:contributor 4        -->  0.1189   |          4.5613           |  1.2000   |    0.0102    |      n/a        |        0.8682        |  0.0058  |
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:Number of reviewers identified: 2
    INFO:__main__:Reviewers: ['contributor 1', 'contributor 2']
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:Human % Tot commits  --> 49.270% |
    INFO:__main__:Bot % Tot commits    --> 50.730% |

Example results (analyze_single_scores=False, detailed_statistics=True, filter_contributors=True)
=================================================================================================

.. code-block:: console

    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:Project                                  --> N.PR Created |N. Commits created | N. PR rev | Mean Time to Review (MTTR) |
    INFO:__main__:<source>/<project-repo>                  -->     215      |       274         |    37     |   1 day, 19:15:01.432432   |
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:
    INFO:__main__:   Author reviews    --> N. PR rev |           MTTR            |  MLenPR   | N. commits c | % Tot Commits c |    Time last rev     |  Score   |
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:contributor 1        -->    10     |  2 days, 8:36:07.200000   |  size/M   |      81      |     29.562    % | 10/06/2019, 07:37:08 |  0.1588  |
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:Reviewed for         -> % PR reviewed
    INFO:__main__:contributor 5        -> 10.000%
    INFO:__main__:contributor 6        -> 10.000%
    INFO:__main__:contributor 2        -> 30.000%
    INFO:__main__:contributor 4        -> 10.000%
    INFO:__main__:contributor 7        -> 20.000%
    INFO:__main__:contributor 3        -> 20.000%
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:contributor 2        -->    18     |  2 days, 1:05:10.388889   |  size/S   |      33      |     12.044    % | 10/18/2019, 06:52:57 |  0.0994  |
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:Reviewed for         -> % PR reviewed
    INFO:__main__:contributor 1        -> 88.889%
    INFO:__main__:contributor 8        -> 5.556%
    INFO:__main__:contributor 3        -> 5.556%
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:contributor 3        -->     5     |      22:33:10.400000      |  size/S   |      3       |     1.095     % | 10/18/2019, 06:51:31 |  0.0109  |
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:Reviewed for         -> % PR reviewed
    INFO:__main__:contributor 1        -> 80.000%
    INFO:__main__:contributor 4        -> 20.000%
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:contributor 4        -->     4     |      9:28:55.500000       |  size/XS  |      2       |     0.730     % | 08/13/2019, 07:35:13 |  0.0058  |
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:Reviewed for         -> % PR reviewed
    INFO:__main__:contributor 1        -> 75.000%
    INFO:__main__:contributor 2        -> 25.000%
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:Number of reviewers identified: 2
    INFO:__main__:Reviewers: ['contributor 1', 'contributor 2']
    INFO:__main__:-----------------------------------------------------------------------------------------------------------------------------------------------
    INFO:__main__:Human % Tot commits  --> 49.270% |
    INFO:__main__:Bot % Tot commits    --> 50.730% |
