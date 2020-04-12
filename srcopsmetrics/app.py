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

import dash
import dash_core_components as dcc
import dash_html_components as html

from typing import Dict

import plotly.graph_objects as go
from flask import Flask, render_template
from pbr.packaging import append_text_list
from plotly.graph_objects import Scatter
from plotly.subplots import make_subplots

from srcopsmetrics.bot_knowledge import github_knowledge, visualization
from srcopsmetrics.github_knowledge_store import GitHubKnowledgeStore
from srcopsmetrics.pre_processing import PreProcessing

pre_process = PreProcessing()

app = Flask(__name__)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


def ttr_in_time(analysed_entities):
    for id in list(analysed_entities.keys()):
        if analysed_entities[id]['closed_at'] is None:
            del analysed_entities[id]

    projects_reviews_data = pre_process.pre_process_prs_project_data(data=analysed_entities)

    prs_created_dts = projects_reviews_data["created_dts"]
    mttr = projects_reviews_data["MTTR"]
    
    data = {"created_dts": prs_created_dts, "MTTR": mttr}
    mttr_in_time_processed = visualization.analyze_outliers(quantity="MTTR", data=data)

    return go.Scatter(x=[el[0] for el in mttr_in_time_processed], y=[el[1] for el in mttr_in_time_processed], name='mean ttr in time', mode='lines+markers')   

def ttci_in_time(analysed_entities):
    for id in list(analysed_entities.keys()):
        if analysed_entities[id]['closed_at'] is None:
            del analysed_entities[id]

    project_issues_data = pre_process.pre_process_issues_project_data(data=analysed_entities)
    issues_created_dts = project_issues_data["created_dts"]
    issues_ttci = project_issues_data["TTCI"]

    data = {"created_dts": issues_created_dts, "TTCI": issues_ttci}
    ttci_per_issue_processed = visualization.analyze_outliers(quantity="TTCI", data=data)

    return go.Scatter(x=[el[0] for el in ttci_per_issue_processed], y=[el[1] for el in ttci_per_issue_processed], name='mean ttci in time', mode='lines+markers')

def overall_entities_status(analysed_entities) -> Dict[str, int]:
        statuses = {}
        for id in analysed_entities.keys():
            status = 'active' if analysed_entities[id]['closed_at'] is None else 'closed'
            if 'merged_at' in analysed_entities[id].keys():
                if analysed_entities[id]['merged_at']:
                    status = 'merged'
                elif status is 'closed':
                    status = 'rejected'
            if status not in statuses.keys():
                statuses[status] = 0
            statuses[status] += 1
        return statuses

def entities(analysed_entities):
    processed = overall_entities_status(analysed_entities)
    labels = list(processed.keys())
    values = list(processed.values())

    return go.Pie(labels=labels, values=values, hole=.3)

def top_x_contributors_activity(issues, prs, x):
    issue_creators = pre_process.pre_process_issues_creators(issues)
    pr_creators = pre_process.pre_process_issues_creators(prs)
    issue_closers = pre_process.pre_process_issues_closers(issues, prs)
    # pr_reviews = pre_process.pre_process_pr_reviews(prs)

    overall_stats = {}
    for issue_creator, pr_creator, issue_closer in zip(issue_creators.keys(), pr_creators.keys(), issue_closers.keys()):
        if issue_creator not in overall_stats.keys():
            overall_stats[issue_creator] = 0
        if issue_closer not in overall_stats.keys():
            overall_stats[issue_closer] = 0
        if pr_creator not in overall_stats.keys():
            overall_stats[pr_creator] = 0
        
        overall_stats[issue_creator] += issue_creators[issue_creator]
        overall_stats[issue_closer] += issue_closers[issue_closer]
        overall_stats[pr_creator] += pr_creators[pr_creator]

    overall_stats = sorted(list(overall_stats.items()), key = lambda contributor: contributor[1], reverse=True)
    top_x_contributors = [el[0] for el in overall_stats[:5]]
    data = []

    data.append(go.Bar(name='issues created', x=top_x_contributors, y=[issue_creators[creator] for creator in top_x_contributors if creator in issue_creators.keys()]))
    data.append(go.Bar(name='issues closed', x=top_x_contributors, y=[issue_closers[closer] for closer in top_x_contributors if closer in issue_closers.keys()]))
    data.append(go.Bar(name='pull requests created', x=top_x_contributors, y=[pr_creators[creator] for creator in top_x_contributors if creator in pr_creators.keys()]))

    fig = go.Figure(data)
    fig.update_layout(barmode='stack', title_text=f'Top {x} active contributors')
    return fig

def general_section(issues, prs):
    fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]], subplot_titles=('Issues', 'Pull Requests'))
    fig.append_trace(entities(issues), row=1, col=1)
    fig.append_trace(entities(prs), row=1, col=2)
    fig.update_layout(title_text='general PR/Issue information')
    return fig

def in_time_section(issues, prs):
    fig = make_subplots(rows=1, cols=2, subplot_titles=('MTTCI', 'MTTR'))
    fig.append_trace(ttci_in_time(issues), row=1, col=1)
    fig.append_trace(ttr_in_time(prs), row=1, col=2)
    fig.update_layout(title_text='in time stats')
    return fig

def contributor_section(issues, pr):
    x = 5
    # fig = make_subplots(rows=1, cols=1, subplot_titles=(f'Top {x} active contributors', 'MTTR'))
    # # metrics = issue closed-1 pt, issue created-1pt, pr-created-1pt, pr-review-1pt
    # fig.append_trace(top_x_contributors_activity(issues, pr, x), row=1, col=1)
    # fig.update_layout(title_text='top 5 active contributors')
    return top_x_contributors_activity(issues, pr, x)

def health_report():
    ghs = GitHubKnowledgeStore(is_local=True)

    issues = ghs.load_previous_knowledge(project_name='AICoE/prometheus-anomaly-detector', knowledge_type='Issue')
    prs = ghs.load_previous_knowledge(project_name='AICoE/prometheus-anomaly-detector', knowledge_type='PullRequest')
    
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

    app.layout = html.Div(children=[
        html.H1(children='Repository Health report'),

        html.Div(children='''
            thoth-station/amun-api
        '''),

        # dcc.Graph(
        #     id='issues',
        #     figure=entities(issues)
        # ),

        # dcc.Graph(
        #     id='pull requests',
        #     figure=entities(prs)
        # ),
        dcc.RangeSlider(
                id='my-range-slider',
                min=0,
                max=20,
                step=0.5,
                value=[5, 15]
        ),
        
        dcc.Graph(
            id='general section',
            figure=general_section(issues, prs),
        ),

        dcc.Graph(
            id='top contributos',
            figure=top_x_contributors_activity(issues, prs, 5)
        ),

        dcc.Graph(
            id='in time',
            figure=in_time_section(issues, prs)
        ),

    ])
    return app
 
health_report().run_server(debug=True)