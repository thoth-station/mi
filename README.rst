================================
Meta-information Indicators (MI)
================================

Overview
========

**MI** project collects data from GitHub repositories. You can use it to either collect data stored locally or within Amazon's S3 cloud.
For personal usage, checkout <Usage> section.

Together with `mi-scheduler <https://github.com/thoth-station/mi-scheduler>`_, we provide automated data extraction pipeline
for data minig of requested repositories and organizations. This pipeline can
be scheduled customly, e.g. to run daily, weekly, and so on.


Data extraction request
-----------------------
To request data extraction for repository or organization,
create **Data Extraction** Issue in **MI-Scheduler** repository. Use this link TODO


Data extraction Pipeline (diagram)
----------------------------------
**MI** pipeline is simple to understand, see diagram below

.. code-block::

                      +---------+
                      |ConfigMap|
                      +----+----+
                           |
                +--+-------+--------+--+
                |  |                |  |
                |  |  mi-scheduler  |  |
                |  |                |  |
                +------+---+---+-------+
                    |   |   |   |    |
                    |   |   |   |    |
                    |   |   |   |    |
                    | Argo Workflows |
                    |   |   |   |    |
                    |   |   |   |    |
    +---------------v---v---v---v----v------------------+                                          +--------------------        +--------------------+
    |                                                   |                                          |   Visualization   |        |   Recommendation   |
    |  +---------+  +---------+            +---------+  |                                          +-------------------+        +--------------------+
    |  |thoth/   |  |  AICoE  |            | your    |  |                                          |   Project Health  |        |   thoth            |
    |  |  station|  |         |            |     org |  |                                          |    (dashboard)    |        |                    |
    |  +---------+  +---------+            +---------+  |                                          |                   |        |                    |
    |  |solver   |  |...      |            |your     |  |                                          +---------+---------+        +----------+---------+
    |  |         |  |         |            |   repos |  |           thoth-station/mi                         ^                             ^
    |  |amun     |  |...      | X X X X X  |         |  |     (Meta-information Indicators)                  |                             |
    |  |         |  |         |            |         |  |                                                    +-------------+---------------+
    |  |adviser  |  |...      |            |         |  |                                                                  |
    |  |         |  |         |            |         |  |                                                                  |
    |  |....     |  |...      |            |         |  |                                                +-----------------+-------------------+
    |  |         |  |         |            |         |  |                                                |                                     |
    |  +---------+  +---------+            +---------+  |                                                |       Knowledge Processsing         |
    |                                                   |                                                |                                     |
    +-----------------------+---------------------------+                                                +-----------------+-------------------+
    GitHub repositories   |                                                                                              ^
                            |                 +--------------------------------------------------------+                   |
                            |                 |                                                        |                   |
                            |                 |      Entities Analysis   +------->      Knowledge      |                   |
                            +---------------->-+                                                      +--------------------+
                                              +---------+----------------+----------+------------------+
                                              |  Issues |  Pull Requests |  Readmes |  etc...........  |
                                              |         |                |          |                  |
                                              +---------+----------------+----------+------------------+



What can **MI** extract from GitHub?
------------------------------------
**MI** analyses entities specified on the srcopsmetrics/entities page
Entity is essentialy a repository metadata that is being inspected (e.g. Issue or Pull Request),
from which specified *features* are extracted and are stored to dataframe.

**MI** is essentialy wrapped around PyGitHub module to provide careless data
extraction with API rate limit handling and data updating.


Install
=======

pip
---

MI is available through PyPI, so you can do

.. code-block:: console

    pip install srcopsmetrics

git
---

Alternatively, you can install srcopsmetrics by cloning repository

.. code-block:: console

    git clone https://github.com/thoth-station/mi.git

    cd mi

    pipenv install --dev


Usage
=====

Setup
-----

To store data locally, use `-l` when calling CLI or set is_local=True when using **MI** as a module.

By default **MI** will try to store the data on Ceph.
In order to store on Ceph you need to provide the following env variables:

- `S3_ENDPOINT_URL` Ceph Host name
- `CEPH_BUCKET` Ceph Bucket name
- `CEPH_BUCKET_PREFIX` Ceph Prefix
- `CEPH_KEY_ID` Ceph Key ID
- `CEPH_SECRET_KEY` Ceph Secret Key

For more information about Ceph storing see `https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html`


CLI
---

See --help for all available options

See some of the examples below

Get repository PullRequest data locally
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

    srcopsmetrics --create --is-local --repository foo_repo --entities PullRequest

which is equivalent to

.. code-block:: console

    srcopsmetrics -clr foo_repo -e PullRequest


Get organization PR data locally
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

    srcopsmetrics -clo foo_org -e PullRequest


Get multiple repository PR data locally
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

    srcopsmetrics -clr foo_repo,bar_repo -e PullRequest


Get multiple entity data locally
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

    srcopsmetrics -clr foo_repo -e PullRequest,Issue,Commit


Meta-Information Entities
=========================
If you want to know more about data analyzed and collected, check `Meta-Information Indicators <https://github.com/thoth-station/mi/tree/master/srcopsmetrics/entities#meta-information-indicators-metrics>`_.


How to contribute
=================
Always feel free to open new Issues or engage in already existing ones!

I want to add new Entity
------------------------
If you want to contribute by adding new entity that will be analysed from GitHub repositories and stored as a knowledge,
your implementation has to meet with Entity criteria described above. Always remember to first create Issue and describe
why do you think this new entity should be analysed and stored and what are the benefits of doing so according to the goal
of thoth-station/mi project. Do not forget to reference the Issue in your Pull Request.
