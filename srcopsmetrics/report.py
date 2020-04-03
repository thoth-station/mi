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

def general_section(issues, prs):
    fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]], subplot_titles=('Issues', 'Pull Requests'))
    fig.append_trace(entities(issues), row=1, col=1)
    fig.append_trace(entities(prs), row=1, col=2)
    fig.update_layout(title_text='general PR/Issue information')
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def in_time_section(issues, prs):
    fig = make_subplots(rows=1, cols=2, subplot_titles=('MTTCI', 'MTTR'))
    fig.append_trace(ttci_in_time(issues), row=1, col=1)
    fig.append_trace(ttr_in_time(prs), row=1, col=2)
    fig.update_layout(title_text='in time stats')
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def generate_report_html():
    ghs = GitHubKnowledgeStore(is_local=True)

    issues = ghs.load_previous_knowledge(project_name='AICoE/prometheus-anomaly-detector', knowledge_type='Issue')
    prs = ghs.load_previous_knowledge(project_name='AICoE/prometheus-anomaly-detector', knowledge_type='PullRequest')

    with open('./srcopsmetrics/templates/report.html', 'w') as f:
        f.write(general_section(issues,prs))
        f.write(in_time_section(issues, prs))

@app.route('/')
def home():
    generate_report_html()
    return render_template('./report.html')

@app.route('/about')
def about():
    return 'about meee'

@app.route('/blog/<blog_id>')
def blogpost(blog_id):
    return f'welcome to {blog_id}' 

if __name__ == '__main__':
    app.run()
