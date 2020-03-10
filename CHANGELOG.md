# Changelog for Thoth's Template GitHub Project

## [0.1.0] - 2019-Sep-11 - goern

### Added

all the things that you see...

## Release 0.1.0 (2020-01-21T16:58:02)
* Revert "Make a new release job in zuul"
* Make a new release job in zuul
* Make a new release job in zuul
* Remove unncecessary comments
* Add Pipfile.lock, set default vals for use_ceph, remove constants
* Satisfy coala
* Satisfy coala
* Support CEPH knowledge loading, minor code refactorings
* Update gitignore
* Remove old src_ops_metrics
* Rename directory to match module name
* Add save knowledge to ceph functionality
* Remove unnecessary imports in init file
* Add setup.py
* :pushpin: Automatic update of dependency pytest from 5.3.3 to 5.3.4
* :pushpin: Automatic update of dependency pytest from 5.3.2 to 5.3.3
* :pushpin: Automatic update of dependency pytest-timeout from 1.3.3 to 1.3.4
* :pushpin: Automatic update of dependency pandas from 0.25.3 to 1.0.0rc0
* :pushpin: Automatic update of dependency pygithub from 1.44.1 to 1.45
* :pushpin: Automatic update of dependency numpy from 1.18.0 to 1.18.1
* Update .zuul.yaml
* Add interactions
* Consider interactions and social factor in reccomendation
* Update README
* Update functions and scores
* Introduce functions to assign size if not provided by label
* Normalize functions
* update README
* Adjust reviewer selection
* Introduce contributor score
* Add project and contributor visualizations
* Introduce CLI and refactor code
* move constants to the beginning
* fix imperatives in docstrings
* staisfy coala requirements
* Reimplement storing PR reviews within PRs themselves
* Fix loading & saving prev knowledge, remove unnecessary code
* Implement pr, pr review and issue information extraction
* remove template dir so the coala can pass
* satisfy coala requirements
* Minor refactor changes in pr_reviewer
* remove toth-pytest completely
* remove thoth-pytest job for kebechet
* recover .zuul config and remove thoth-pytest job from it
* satisfy coala requirements
* fix comment typo
* remove zuul job
* fix no new knowledge guard
* add type hints
* remove update knowledge parameter
* make loggers use c-style formatted strings
* remove token information
* fix issues pointed out by francesco
* Correct typo in CODEOWNERS
* Update CODEOWNERS
* Remove loggers in the guards
* Refactor gathering pull request code to be more readable
* Collect and analyze stastistics on Project repositories from GitHub

## Release 0.2.0 (2020-01-21T20:55:55)
* Rename dirs to match snake_case, gitignore additions
* Fix README in setup.py
* Edit README in setup.py for PyPI long_description compatibility
* Fix local module imports

## Release 0.2.1 (2020-01-22T11:18:04)
* Fix intendation error from rstcheck

## Release 0.2.2 (2020-01-22T16:41:58)
* Increase timeout to 50ms
* Refactor src_ops_metrics to srcopsmetrics

## Release 0.2.3 (2020-02-11T21:18:45)
* Update .thoth.yaml
* :pushpin: Automatic update of dependency pygithub from 1.45 to 1.46
* :pushpin: Automatic update of dependency thoth-storages from 0.21.11 to 0.22.0
* :pushpin: Automatic update of dependency pandas from 1.0.0 to 1.0.1
* :pushpin: Automatic update of dependency matplotlib from 3.2.0rc1 to 3.2.0rc3
* :pushpin: Automatic update of dependency pandas from 1.0.0rc0 to 1.0.0
* :pushpin: Automatic update of dependency pytest from 5.3.4 to 5.3.5
* :pushpin: Automatic update of dependency thoth-storages from 0.21.10 to 0.21.11
* Satysify coala
* Fix errors after refactorings
* Fix issue analysis and docstrings
* Fix docstrings
* Add docstrings and fix typos
* Add alias for --projects argument
* Add API rate limit check and wait

## Release 1.0.0 (2020-02-26T23:49:29)
* Remove static method from _visualize_ttci_wrt_labels
* Add StatisticalQuantity Enum and adjust Schema
* Adjust docstring for GitHubKnowledge Class
* Adjust Schema names
* Divide classes by context
* :pushpin: Automatic update of dependency thoth-storages from 0.22.2 to 0.22.3
* :pushpin: Automatic update of dependency plotly from 4.5.1 to 4.5.2
* :pushpin: Automatic update of dependency plotly from 4.5.0 to 4.5.1
* Fix CEPH to be working and used by default
* Fix mistakes in utils
* Document & refactor
* Fix developer vizs
* Minor refactor changes
* Add notebook plotting compatibility
* Add TTCI viz for labels and project comparisson
* :pushpin: Automatic update of dependency thoth-storages from 0.22.1 to 0.22.2
* Satisfy coala only for visualization.py
* Add overall top x issues types for project viz
* Add refactor lib rope for dev
* Add top X issue types viz
* Fix issue type viz and slight refactor for methods
* Add new viz for issue labels and fix previous one
* :pushpin: Automatic update of dependency thoth-storages from 0.22.0 to 0.22.1
* Add top X issue interactions visualization
* Add plotly into dependencies
* Add issues closed and single interactions visualizations
* Fix comment block mistake
* Satisfy the last coala reqs
* Satisfy coala
* Fix TTCI measurement metrics and storage
* Add TTCI plots for visualization

## Release 1.0.1 (2020-03-10T19:42:51)
* :pushpin: Automatic update of dependency matplotlib from 3.2.0rc3 to 3.2.0
* Remove unnecessary line
* Clear more unused stuff
* Remove unused imports, add warning, fix cli reccomender
* Move get_repositories to github_knowledge
* satisfy coala
* Move get_repositories to utisl
* satisfy coala
* Add secret & configmap template
* Add templates for build and imgStream
* Fix viz in cli for orgs and repos
* Satisfy coala
* Add cronjob template
* Remove project, implement org and repo option
* Add annotations for reminding templates
* Add description and change ninja templ version
* Add skelet for various entities
* Add configMap configurations
* Fix template intendation structure
* Add yaml configs for openshift
* Add envvars options to cli tool
* Add yamls for openshift cronjob

## Release 1.0.2 (2020-03-10T20:26:57)
* Release of version 1.0.1
* :pushpin: Automatic update of dependency matplotlib from 3.2.0rc3 to 3.2.0
* Remove unnecessary line
* Clear more unused stuff
* Remove unused imports, add warning, fix cli reccomender
* Move get_repositories to github_knowledge
* satisfy coala
* Move get_repositories to utisl
* satisfy coala
* Add secret & configmap template
* Add templates for build and imgStream
* Fix viz in cli for orgs and repos
* Satisfy coala
* Add cronjob template
* Remove project, implement org and repo option
* Add annotations for reminding templates
* Add description and change ninja templ version
* Add skelet for various entities
* Add configMap configurations
* Fix template intendation structure
* Add yaml configs for openshift
* Add envvars options to cli tool
* Add yamls for openshift cronjob
* Release of version 1.0.0
* Remove static method from _visualize_ttci_wrt_labels
* Add StatisticalQuantity Enum and adjust Schema
* Adjust docstring for GitHubKnowledge Class
* Adjust Schema names
* Divide classes by context
* :pushpin: Automatic update of dependency thoth-storages from 0.22.2 to 0.22.3
* :pushpin: Automatic update of dependency plotly from 4.5.1 to 4.5.2
* :pushpin: Automatic update of dependency plotly from 4.5.0 to 4.5.1
* Fix CEPH to be working and used by default
* Fix mistakes in utils
* Document & refactor
* Fix developer vizs
* Minor refactor changes
* Add notebook plotting compatibility
* Add TTCI viz for labels and project comparisson
* :pushpin: Automatic update of dependency thoth-storages from 0.22.1 to 0.22.2
* Satisfy coala only for visualization.py
* Add overall top x issues types for project viz
* Add refactor lib rope for dev
* Add top X issue types viz
* Fix issue type viz and slight refactor for methods
* Add new viz for issue labels and fix previous one
* :pushpin: Automatic update of dependency thoth-storages from 0.22.0 to 0.22.1
* Add top X issue interactions visualization
* Add plotly into dependencies
* Add issues closed and single interactions visualizations
* Release of version 0.2.3
* Update .thoth.yaml
* Fix comment block mistake
* Satisfy the last coala reqs
* Satisfy coala
* Fix TTCI measurement metrics and storage
* :pushpin: Automatic update of dependency pygithub from 1.45 to 1.46
* :pushpin: Automatic update of dependency thoth-storages from 0.21.11 to 0.22.0
* :pushpin: Automatic update of dependency pandas from 1.0.0 to 1.0.1
* :pushpin: Automatic update of dependency matplotlib from 3.2.0rc1 to 3.2.0rc3
* :pushpin: Automatic update of dependency pandas from 1.0.0rc0 to 1.0.0
* :pushpin: Automatic update of dependency pytest from 5.3.4 to 5.3.5
* :pushpin: Automatic update of dependency thoth-storages from 0.21.10 to 0.21.11
* Add TTCI plots for visualization
* Satysify coala
* Fix errors after refactorings
* Fix issue analysis and docstrings
* Fix docstrings
* Add docstrings and fix typos
* Add alias for --projects argument
* Add API rate limit check and wait
* Release of version 0.2.2
* Increase timeout to 50ms
* Release of version 0.2.1
* Refactor src_ops_metrics to srcopsmetrics
* Fix intendation error from rstcheck
* Release of version 0.2.0
* Rename dirs to match snake_case, gitignore additions
* Fix README in setup.py
* Edit README in setup.py for PyPI long_description compatibility
* Fix local module imports
* Release of version 0.1.0
* Revert "Make a new release job in zuul"
* Make a new release job in zuul
* Make a new release job in zuul
* Remove unncecessary comments
* Add Pipfile.lock, set default vals for use_ceph, remove constants
* Satisfy coala
* Satisfy coala
* Support CEPH knowledge loading, minor code refactorings
* Update gitignore
* Remove old src_ops_metrics
* Rename directory to match module name
* Add save knowledge to ceph functionality
* Remove unnecessary imports in init file
* Add setup.py
* :pushpin: Automatic update of dependency pytest from 5.3.3 to 5.3.4
* :pushpin: Automatic update of dependency pytest from 5.3.2 to 5.3.3
* :pushpin: Automatic update of dependency pytest-timeout from 1.3.3 to 1.3.4
* :pushpin: Automatic update of dependency pandas from 0.25.3 to 1.0.0rc0
* :pushpin: Automatic update of dependency pygithub from 1.44.1 to 1.45
* :pushpin: Automatic update of dependency numpy from 1.18.0 to 1.18.1
* Update .zuul.yaml
* Add interactions
* Consider interactions and social factor in reccomendation
* Update README
* Update functions and scores
* Introduce functions to assign size if not provided by label
* Normalize functions
* update README
* Adjust reviewer selection
* Introduce contributor score
* Add project and contributor visualizations
* Introduce CLI and refactor code
* move constants to the beginning
* fix imperatives in docstrings
* staisfy coala requirements
* Reimplement storing PR reviews within PRs themselves
* Fix loading & saving prev knowledge, remove unnecessary code
* Implement pr, pr review and issue information extraction
* remove template dir so the coala can pass
* satisfy coala requirements
* Minor refactor changes in pr_reviewer
* remove toth-pytest completely
* remove thoth-pytest job for kebechet
* recover .zuul config and remove thoth-pytest job from it
* satisfy coala requirements
* fix comment typo
* remove zuul job
* fix no new knowledge guard
* add type hints
* remove update knowledge parameter
* make loggers use c-style formatted strings
* remove token information
* fix issues pointed out by francesco
* Correct typo in CODEOWNERS
* Update CODEOWNERS
* Remove loggers in the guards
* Refactor gathering pull request code to be more readable
* Collect and analyze stastistics on Project repositories from GitHub
