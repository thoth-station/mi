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

from srcopsmetrics.bot_knowledge import github_knowledge
from srcopsmetrics.github_knowledge_store import GitHubKnowledgeStore

app = Flask(__name__)

def overall_entities_status(analysed_entities) -> Dict[str, int]:
        statuses = {}
        for id in analysed_entities.keys():
            status = 'active' if analysed_entities[id]['closed_at'] is None else 'closed'
            if status not in statuses.keys():
                statuses[status] = 0
            statuses[status] += 1
        return statuses

def entities(analysed_entities):
    processed = overall_entities_status(analysed_entities)
    labels = list(processed.keys())
    values = list(processed.values())

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
    fig.write_html(file='./srcopsmetrics/templates/report.html')

@app.route('/')
def home():
    ghs = GitHubKnowledgeStore(is_local=True)
    knowledge = ghs.load_previous_knowledge(project_name='AICoE/prometheus-anomaly-detector', knowledge_type='Issue')

    entities(analysed_entities=knowledge)
    return render_template('./report.html')

@app.route('/about')
def about():
    return 'about meee'

@app.route('/blog/<blog_id>')
def blogpost(blog_id):
    return f'welcome to {blog_id}' 

if __name__ == '__main__':
    app.run()
