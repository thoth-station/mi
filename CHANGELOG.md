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

## Release 2.0.0 (2020-05-14T21:08:01)
* :pushpin: Automatic update of dependency thoth-storages from 0.22.9 to 0.22.10
* Fix processing, add more labels
* :pushpin: Automatic update of dependency plotly from 4.7.0 to 4.7.1
* :pushpin: Automatic update of dependency pytest from 5.4.1 to 5.4.2
* :pushpin: Automatic update of dependency plotly from 4.6.0 to 4.7.0
* Fix in time stats
* Fix my code weirdness!
* correct typo
* :pushpin: Automatic update of dependency rope from 0.16.0 to 0.17.0
* change doc
* Raise error for org viz
* remove html render
* remove unnecessary file
* Implement working dash report page.
* :pushpin: Automatic update of dependency numpy from 1.18.3 to 1.18.4
* :pushpin: Automatic update of dependency pygithub from 1.50 to 1.51
* add doc
* Make -c flag remove processed knowledge
* :pushpin: Automatic update of dependency thoth-storages from 0.22.8 to 0.22.9
* :pushpin: Automatic update of dependency thoth-storages from 0.22.7 to 0.22.8
* :pushpin: Automatic update of dependency pygithub from 1.47 to 1.50
* remove old app
* Add new pipfiles
* rename app to report
* Remove old Flask report
* Missing character
* complete basic dash report
* add dash app demo
* Add in time section
* add general pr/issue info section
* init commit, raw ideas in code
* add contributor section
* complete basic dash report
* remove generated report file
* add dash app demo
* Add topx active contbrs to report
* Add in time section
* add general pr/issue info section
* add basic report
* init commit, raw ideas in code
* Add newline to exceptions
* Add docstring to help
* Add docstring to help
* Add doc
* Implement feature
* Format and add doc
* remove prepocessed dir
* Rebase
* Fix loading&storing issues
* Implement and use ProcessedStorage decorator
* Refactor viz partially
* Partially refactore pre_processing
* Fix loading&storing issues
* Implement and use ProcessedStorage decorator
* :pushpin: Automatic update of dependency autopep8 from 1.5.1 to 1.5.2
* :pushpin: Automatic update of dependency numpy from 1.18.2 to 1.18.3
* Fix unintended text
* Refactor viz partially
* Make section entity
* Add How to contribute section
* Partially refactore pre_processing
* Fix viz error
* Add tutorial on how to add new entity
* satisfy coala
* Remove unusued variable
* Add schema for entity
* Adjust enums type
* Introduce ContentFile entity to collect README files initially
* Change main viz functions to behave as before
* Fix visualization api
* add one self reference to get_referenced_issues
* Recover prev pipfiles
* Undo Pipfile removal
* Add problem occured log
* remove static from get_referenced_issues
* Add dots
* satisfy coala
* Rename occurences in other modules
* remove old github_knowledge_store
* Change GithubKnowledgeStore to contain only iterting thru analysis
* Make standalone class for storage handling
* Fix schemas to work
* change schema names
* Fix issue linking with pr body
* remove unnecessary quotes
* :pushpin: Automatic update of dependency autopep8 from 1.5 to 1.5.1
* Add missing plots list to README
* Update README
* Follow standards
* :pushpin: Automatic update of dependency plotly from 4.5.4 to 4.6.0
* store issue ids as str in dict
* :pushpin: Automatic update of dependency thoth-storages from 0.22.6 to 0.22.7
* satisfy coala
* Make logger pretty again, fix unknown bug
* :pushpin: Automatic update of dependency thoth-storages from 0.22.5 to 0.22.6
* fix secrets and config name + fix cli call
* :pushpin: Automatic update of dependency thoth-storages from 0.22.3 to 0.22.5
* :pushpin: Automatic update of dependency pandas from 1.0.2 to 1.0.3
* :pushpin: Automatic update of dependency matplotlib from 3.2.0 to 3.2.1
* :pushpin: Automatic update of dependency numpy from 1.18.1 to 1.18.2
* :pushpin: Automatic update of dependency pandas from 1.0.1 to 1.0.2
* :pushpin: Automatic update of dependency pygithub from 1.46 to 1.47
* :pushpin: Automatic update of dependency pytest from 5.4.0 to 5.4.1
* :pushpin: Automatic update of dependency pytest from 5.3.5 to 5.4.0
* :pushpin: Automatic update of dependency plotly from 4.5.3 to 4.5.4
* :pushpin: Automatic update of dependency plotly from 4.5.2 to 4.5.3

## Release 2.0.1 (2020-07-14T14:33:46)
* pre-commit config added (#164)
* Update OWNERS
* Create OWNERS
* :pushpin: Automatic update of dependency numpy from 1.18.5 to 1.19.0
* :pushpin: Automatic update of dependency numpy from 1.18.5 to 1.19.0
* :pushpin: Automatic update of dependency dash from 1.13.2 to 1.13.3
* :pushpin: Automatic update of dependency dash from 1.13.1 to 1.13.2
* :pushpin: Automatic update of dependency dash from 1.13.1 to 1.13.2
* :pushpin: Automatic update of dependency pandas from 1.0.4 to 1.0.5
* :pushpin: Automatic update of dependency pandas from 1.0.4 to 1.0.5
* :pushpin: Automatic update of dependency thoth-storages from 0.23.0 to 0.23.2
* :pushpin: Automatic update of dependency thoth-storages from 0.23.0 to 0.23.2
* Fix reviewers stack bar
* Fix processing on Ceph
* Do not use pre-preleases
* :pushpin: Automatic update of dependency coala-bears from 0.12.0.dev20171110210444 to 0.11.1
* :pushpin: Automatic update of dependency numpy from 1.19.0rc2 to 1.18.5
* add processed repo
* Add pipfile.lock
* :pushpin: Automatic update of dependency coala-bears from 0.12.0.dev20171110210444 to 0.11.1
* :pushpin: Automatic update of dependency pytest-cov from 2.9.0 to 2.10.0
* :pushpin: Automatic update of dependency numpy from 1.19.0rc2 to 1.18.5
* :pushpin: Automatic update of dependency thoth-storages from 0.22.12 to 0.23.0
* :pushpin: Automatic update of dependency thoth-storages from 0.22.12 to 0.23.0
* add ttl and generateName
* added a 'tekton trigger tag_release pipeline issue'
* implement final template structure
* Correct setup
* Parameterize steps
* Move parameters to openshift templtate
* Remove viz step
* :pushpin: Automatic update of dependency pytest from 5.4.2 to 5.4.3
* :pushpin: Automatic update of dependency numpy from 1.19.0rc1 to 1.19.0rc2
* :pushpin: Automatic update of dependency autopep8 from 1.5.2 to 1.5.3
* :pushpin: Automatic update of dependency thoth-storages from 0.22.11 to 0.22.12
* Add dag task
* init structure of the workflow template
* :pushpin: Automatic update of dependency pandas from 1.0.3 to 1.0.4
* :pushpin: Automatic update of dependency plotly from 4.8.0 to 4.8.1
* :pushpin: Automatic update of dependency plotly from 4.7.1 to 4.8.0
* :pushpin: Automatic update of dependency pytest-cov from 2.8.1 to 2.9.0
* :pushpin: Automatic update of dependency thoth-storages from 0.22.10 to 0.22.11
* Add steps
* :pushpin: Automatic update of dependency numpy from 1.18.4 to 1.19.0rc1
* Add image envs
* Add basic structure
* Fix code block
* Fix bulletpoints
* Fix readme to be rst

## Release 2.1.0 (2020-11-11T14:36:43)
### Features
* Add christoph as approver (#282)
* Fix/kebechet update entity (#280)
* Remove unnecesary multiple initializations (#281)
* Fix local&remote knowledge store%load, init knowledge in iterator (#277)
* Add Commits as entities (#276)
* Add Forks as features (#268)
* Fix stargazers (#266)
* Fix/cached knowledge (#263)
* Add Release entity (#253)
* Feature/kebechet update manager (#251)
* Rename current contentfile to ReadMe (#252)
* Add Stars as Entity (#255)
* Update issue templates from template project (#254)
* Entities Concept Code Refactor (#186)
* Clear errors issued by pre-commit (visualizations and report excluded) (#179)
* Remove visualizations (#180)
* Feature/storage path env var (#168)
* Add diagram & note (#174)
* deploy the image to mi imagestream
### Bug Fixes
* Remove coala, fix pipenv update (#181)
### Improvements
* Store additions and deletions for every week (#275)
* Remove plotly and dash, visualizations no longer present (#259)
### Automatic Updates
* :pushpin: Automatic update of dependency thoth-storages from 0.26.0 to 0.26.1 (#283)
* :pushpin: Automatic update of dependency thoth-storages from 0.25.16 to 0.26.0 (#279)
* :pushpin: Automatic update of dependency thoth-storages from 0.25.15 to 0.25.16 (#274)
* :pushpin: Automatic update of dependency thoth-storages from 0.25.15 to 0.25.16 (#273)
* :pushpin: Automatic update of dependency thoth-storages from 0.25.15 to 0.25.16 (#272)
* :pushpin: Automatic update of dependency pandas from 1.1.3 to 1.1.4 (#271)
* :pushpin: Automatic update of dependency pandas from 1.1.3 to 1.1.4 (#270)
* :pushpin: Automatic update of dependency numpy from 1.19.3 to 1.19.4 (#269)
* :pushpin: Automatic update of dependency pytest from 6.1.1 to 6.1.2 (#267)
* :pushpin: Automatic update of dependency pytest from 6.1.1 to 6.1.2 (#265)
* :pushpin: Automatic update of dependency numpy from 1.19.2 to 1.19.3 (#264)
* :pushpin: Automatic update of dependency dash from 1.16.2 to 1.16.3 (#247)
* :pushpin: Automatic update of dependency dash from 1.16.2 to 1.16.3 (#246)
* :pushpin: Automatic update of dependency rope from 0.17.0 to 0.18.0 (#245)
* :pushpin: Automatic update of dependency rope from 0.17.0 to 0.18.0 (#244)
* :pushpin: Automatic update of dependency rope from 0.17.0 to 0.18.0 (#243)
* :pushpin: Automatic update of dependency pytest from 6.0.2 to 6.1.1 (#241)
* :pushpin: Automatic update of dependency pytest from 6.0.2 to 6.1.1 (#240)
* :pushpin: Automatic update of dependency plotly from 4.10.0 to 4.11.0 (#239)
* :pushpin: Automatic update of dependency pytest from 6.0.2 to 6.1.1 (#238)
* :pushpin: Automatic update of dependency plotly from 4.10.0 to 4.11.0 (#237)
* :pushpin: Automatic update of dependency plotly from 4.10.0 to 4.11.0 (#236)
* :pushpin: Automatic update of dependency thoth-storages from 0.25.11 to 0.25.15 (#235)
* :pushpin: Automatic update of dependency thoth-storages from 0.25.11 to 0.25.15 (#234)
* :pushpin: Automatic update of dependency pandas from 1.1.2 to 1.1.3 (#233)
* :pushpin: Automatic update of dependency dash from 1.16.1 to 1.16.2 (#232)
* :pushpin: Automatic update of dependency dash from 1.16.1 to 1.16.2 (#231)
* :pushpin: Automatic update of dependency dash from 1.16.1 to 1.16.2 (#230)
* :pushpin: Automatic update of dependency dash from 1.16.1 to 1.16.2 (#229)
* :pushpin: Automatic update of dependency dash from 1.16.1 to 1.16.2 (#228)
* :pushpin: Automatic update of dependency dash from 1.14.0 to 1.16.1 (#225)
* :pushpin: Automatic update of dependency dash from 1.14.0 to 1.16.1 (#224)
* :pushpin: Automatic update of dependency pytest from 6.0.1 to 6.0.2 (#223)
* :pushpin: Automatic update of dependency pytest from 6.0.1 to 6.0.2 (#222)
* :pushpin: Automatic update of dependency dash from 1.14.0 to 1.16.1 (#221)
* :pushpin: Automatic update of dependency pytest from 6.0.1 to 6.0.2 (#220)
* :pushpin: Automatic update of dependency pytest from 6.0.1 to 6.0.2 (#219)
* :pushpin: Automatic update of dependency dash from 1.14.0 to 1.16.1 (#218)
* :pushpin: Automatic update of dependency plotly from 4.9.0 to 4.10.0 (#217)
* :pushpin: Automatic update of dependency dash from 1.14.0 to 1.16.1 (#216)
* :pushpin: Automatic update of dependency dash from 1.14.0 to 1.16.1 (#215)
* :pushpin: Automatic update of dependency dash from 1.14.0 to 1.16.1 (#214)
* :pushpin: Automatic update of dependency dash from 1.14.0 to 1.16.1 (#213)
* :pushpin: Automatic update of dependency plotly from 4.9.0 to 4.10.0 (#212)
* :pushpin: Automatic update of dependency plotly from 4.9.0 to 4.10.0 (#211)
* :pushpin: Automatic update of dependency thoth-storages from 0.25.3 to 0.25.11 (#210)
* :pushpin: Automatic update of dependency thoth-storages from 0.25.3 to 0.25.11 (#209)
* :pushpin: Automatic update of dependency plotly from 4.9.0 to 4.10.0 (#205)
* :pushpin: Automatic update of dependency thoth-storages from 0.25.3 to 0.25.11 (#203)
* :pushpin: Automatic update of dependency matplotlib from 3.3.1 to 3.3.2 (#208)
* :pushpin: Automatic update of dependency matplotlib from 3.3.1 to 3.3.2 (#207)
* :pushpin: Automatic update of dependency pandas from 1.1.1 to 1.1.2 (#206)
* :pushpin: Automatic update of dependency matplotlib from 3.3.1 to 3.3.2 (#200)
* :pushpin: Automatic update of dependency pandas from 1.1.1 to 1.1.2 (#201)
* :pushpin: Automatic update of dependency numpy from 1.19.1 to 1.19.2 (#199)
* :pushpin: Automatic update of dependency thoth-storages from 0.25.1 to 0.25.3 (#197)
* :pushpin: Automatic update of dependency pandas from 1.1.0 to 1.1.1 (#196)
* :pushpin: Automatic update of dependency thoth-storages from 0.25.1 to 0.25.3 (#195)
* :pushpin: Automatic update of dependency thoth-storages from 0.25.1 to 0.25.3 (#194)
* :pushpin: Automatic update of dependency pandas from 1.1.0 to 1.1.1 (#193)
* :pushpin: Automatic update of dependency pandas from 1.1.0 to 1.1.1 (#192)
* :pushpin: Automatic update of dependency pandas from 1.1.0 to 1.1.1 (#191)
* :pushpin: Automatic update of dependency pygithub from 1.52 to 1.53 (#190)
* :pushpin: Automatic update of dependency pygithub from 1.52 to 1.53 (#189)
* :pushpin: Automatic update of dependency pytest-cov from 2.10.0 to 2.10.1 (#185)
* :pushpin: Automatic update of dependency pytest-cov from 2.10.0 to 2.10.1 (#184)
* :pushpin: Automatic update of dependency thoth-storages from 0.25.0 to 0.25.1 (#183)
* :pushpin: Automatic update of dependency matplotlib from 3.3.0 to 3.3.1 (#182)

## Release 2.2.0 (2020-12-01T21:40:58)
### Features
* bump python version (#292)
* Add specific labels to issues (#286)
* :arrow_up: Automatic update of dependencies by kebechet. (#291)
* Fix/dependency update author (#290)
* :arrow_up: Automatic update of dependencies by kebechet. (#288)

## Release 2.3.0 (2021-01-22T00:44:31)
### Features
* PullRequestDiscussion entity (#302)
* :arrow_up: Automatic update of dependencies by kebechet. (#307)
* :arrow_up: Automatic update of dependencies by kebechet. (#306)
* add dominik to approvers (#305)
* :arrow_up: Automatic update of dependencies by kebechet. (#304)
* Add explicitly thoth-pytest38 (#303)
* Fix graph (#297)
* Multiple entities now passed as comma sep. string (#296)
### Improvements
* Add title and body attributes for inspection (#298)

## Release 2.3.1 (2021-01-29T10:47:25)
### Features
* Check if readme exists (#319)
* Check that patch can be None (#320)
* :arrow_up: Automatic update of dependencies by kebechet. (#312)
### Improvements
* Add requirements for PyPI, remove unnecessary dependencies (#310)

## Release 2.3.2 (2021-03-25T22:20:35)
### Features
* Allow setting cli options by envvars (#348)
* :arrow_up: Automatic update of dependencies by Kebechet (#347)
* Documentation/metrics (#316)
* Add .prow (#344)
* Add metrics/scores evaluation and cli option (#333)
* :arrow_up: Automatic update of dependencies by Kebechet (#330)
### Improvements
* Add Kebechet metrics class and cli option (#332)

## Release 2.3.3 (2021-03-29T14:23:06)
### Features
* Fix local loading (#353)
* Fix issue body, make it optional (#351)

## Release 2.3.4 (2021-03-30T13:25:11)
### Features
* Include empty repo check (#357)

## Release 2.4.0 (2021-04-07T14:10:03)
### Features
* Add statistics aggregation for daily data (#364)
* :arrow_up: Automatic update of dependencies by Kebechet (#365)
* Remove codeowners file (#362)
* Support multiple repositories (#361)
