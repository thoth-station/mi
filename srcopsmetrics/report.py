#!/usr/bin/env python3
# SrcOpsMetrics
# Copyright (C) 2020 Dominik Tuchyna
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Report page running on Dash."""

import os
from typing import Dict

import dash
import dash_core_components as dcc
import dash_html_components as html

import plotly.graph_objects as go
from plotly.graph_objects import Scatter
from plotly.subplots import make_subplots

from srcopsmetrics import visualization
from srcopsmetrics.enums import EntityTypeEnum
from srcopsmetrics.processing import Processing
from srcopsmetrics.storage import KnowledgeStorage
from srcopsmetrics.visualization import Visualization


class Report:
    """Customized health report in form of Dash application running on localhost."""

    def __init__(self, project_name: str):
        """Initialize with project name."""
        self.project_name = project_name

        store = KnowledgeStorage(os.getenv("IS_LOCAL"))
        prs = store.load_previous_knowledge(project_name=project_name, knowledge_type=EntityTypeEnum.PULL_REQUEST.value)
        issues = store.load_previous_knowledge(project_name=project_name, knowledge_type=EntityTypeEnum.ISSUE.value)

        self.viz = Visualization(processing=Processing(pull_requests=prs, issues=issues))

        external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
        self.app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
        self.app.config.suppress_callback_exceptions = True

    def launch(self):
        """Launch report as generated."""
        app = self.app

        @app.callback(
            dash.dependencies.Output("issue-opener", "figure"), [dash.dependencies.Input("demo-dropdown", "value")]
        )
        def update_opener(value):
            return self.viz._visualize_issues_types_given_developer(author_login_id=value, developer_action="Open")

        @app.callback(
            dash.dependencies.Output("issue-closer", "figure"), [dash.dependencies.Input("demo-dropdown", "value")]
        )
        def update_closer(value):
            return self.viz._visualize_issues_types_given_developer(author_login_id=value, developer_action="Close")

        @app.callback(dash.dependencies.Output("inter", "figure"), [dash.dependencies.Input("demo-dropdown", "value")])
        def update_inter(value):
            return self.viz._visualize_issue_interactions(author_login_id=value)

        self.generate_health_report()
        self.app.run_server(debug=True)

    def generate_health_report(self):
        """Generate content for report page."""
        pr_creators = self.viz.processing.process_issues_creators()
        issue_creators = self.viz.processing.process_issues_creators()

        # min_date = min(self.viz.processing.issues.values(), key= lambda issue: int(issue['created_at']))
        # max_date = max(self.viz.processing.issues.values(), key= lambda issue: int(issue['created_at']))

        self.app.layout = html.Div(
            children=[
                html.Center(html.H1(children=f"GitHub repository {self.project_name} Health Report")),
                # html.Div(children=f'''
                #     {self.project_name}
                # '''),
                # dcc.RangeSlider(
                #     id='time-setter',
                #     min=min_date,
                #     max=max_date,
                #     step=1,
                #     # value=[5, 15],
                # ),
                html.Center(html.H2(children=f"General PR/Issue information")),
                dcc.Graph(id="general section", figure=self.general_section(),),
                html.Center(html.H2(children=f"Repository in time")),
                dcc.Graph(id="in time", figure=self.in_time_section()),
                html.Center(html.H2(children=f"Label correlations")),
                dcc.Graph(id="labels", figure=self.viz._visualize_ttci_wrt_labels()),
                html.Center(html.H2(children=f"What about contributors?")),
                dcc.Graph(id="contributos", figure=self.contributor_section(5)),
                dcc.Dropdown(
                    id="demo-dropdown",
                    options=[{"label": i, "value": i} for i in issue_creators],
                    value=list(issue_creators.keys())[0],
                ),
                html.Div(id="dd-output-container"),
                dcc.Graph(id="issue-opener"),
                dcc.Graph(id="issue-closer"),
                dcc.Graph(id="inter"),
            ]
        )

    def general_section(self):
        """Generate general (first) section to the report."""
        fig = make_subplots(
            rows=1, cols=2, specs=[[{"type": "domain"}, {"type": "domain"}]], subplot_titles=("Issues", "Pull Requests")
        )

        fig.append_trace(self.viz.pie_chart_entities("Issue"), row=1, col=1)
        fig.append_trace(self.viz.pie_chart_entities("PullRequest"), row=1, col=2)

        return fig

    def in_time_section(self):
        """Generate in time (second) section to report."""
        fig = make_subplots(rows=1, cols=2, subplot_titles=("MTTCI", "MTTR"))

        fig.append_trace(self.viz.scatter_ttci_in_time(), row=1, col=1)
        fig.append_trace(self.viz.scatter_ttr_in_time(), row=1, col=2)
        fig.update_layout(yaxis_title="hours")

        return fig

    def contributor_section(self, x: int):
        """Generate contributors (last) section to the report.

        param:x:int top X developers will be available for render
        """
        return self.viz.stack_chart_top_x_contributors_activity(x)
